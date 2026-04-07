"""
DeepResearcher v2: H100-Optimized Math Research Agent

Major upgrades over v1:
    - Model: DS-R1-Distill-Qwen-32B-AWQ (2.2x faster, higher pass@1 than 70B)
    - Majority voting: Generate N solutions, take consensus answer
    - Tool-Integrated Reasoning (TIR): Execute code mid-generation
    - Natural Language Verifier: Catch logic errors code can't detect
    - Balanced prompting: Anti-confirmation bias (from Gemini Deep Think)
    - Dynamic time allocation: Spend more time on harder problems
    - Auto-detect chat template (Qwen vs Llama)
    - Higher token limits (8192+ for long reasoning chains)

Usage (Kaggle Notebook):
    researcher = DeepResearcher(
        model_path="/kaggle/input/aimo-model-32b-awq/",
        time_limit_hours=4.5,
        num_samples=16,
    )
    researcher.run(problems, "/kaggle/working/research_data.jsonl")
"""

from __future__ import annotations

import json
import logging
import re
import time
from collections import Counter
from dataclasses import dataclass, field, asdict
from pathlib import Path

from agent.harmony_layer import HarmonyServer
from agent.sandbox import run_verification, extract_code_blocks
from agent.geometry_prompts import (
    build_alpha_geometry_formalization_prompt,
    extract_formal_geometry_problem,
)
from agent.blueprint_generator import (
    MathBlueprint,
    parse_blueprint,
    build_blueprint_generation_prompt,
    build_blueprint_execution_prompt,
    SELF_REFLECT_PROMPT,
)

from src.critique.flaw_detector import FlawDetector
from src.models.critique import FlawCode
from src.models.solution import SolutionTrace
from src.models.trace import VerificationStatus
from src.models.verification import ConfidenceLevel, VerificationReport
from src.geometry import AlphaGeometryRESolver
from src.verification.pipeline import VerificationPipeline

try:
    from src.solver.answer_selector import AnnotatedSolution, AnswerSelector
    _HAS_ANSWER_SELECTOR = True
except ImportError:
    _HAS_ANSWER_SELECTOR = False

try:
    from src.solver.confidence_scorer import score_trace, TraceConfidence
    _HAS_CONFIDENCE_SCORER = True
except ImportError:
    _HAS_CONFIDENCE_SCORER = False

from agent.prompts import (
    build_system_prompt,
    build_generate_prompt,
    build_verify_prompt,
    build_nl_verify_prompt,
    build_correct_prompt,
    build_approach_prompt,
    build_revise_prompt,
    build_iterative_refine_prompt,
    extract_answer,
    extract_nl_verdict,
    detect_model_family,
    format_tir_continuation,
    classify_topic,
    TOPIC_PATCHES,
    APPROACH_FRAMEWORKS,
    APPROACH_KEYS,
)

logger = logging.getLogger(__name__)

_answer_selector = AnswerSelector() if _HAS_ANSWER_SELECTOR else None


# =============================================================================
# Exceptions
# =============================================================================

class TimeLimitExceeded(Exception):
    """Raised when the hard timer triggers a graceful exit."""
    pass


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Attempt:
    """A single generate/correct attempt within a research cycle.

    Attributes:
        attempt_number (int): The sequential attempt number.
        solution_text (str): The raw text of the model's generated solution.
        extracted_answer (str | None): The answer extracted using regex.
        code_blocks_found (int): Number of Python code blocks extracted.
        verification_passed (bool): Whether the sandbox executed the code without errors.
        verification_output (str): The combined stdout/stderr from the sandbox.
        nl_verification (str): Output from the optional natural language verifier.
        duration_seconds (float): Time taken for this specific attempt.
    """
    attempt_number: int
    solution_text: str
    extracted_answer: str | None
    code_blocks_found: int
    verification_passed: bool
    verification_output: str
    nl_verification: str = ""
    duration_seconds: float = 0.0
    approach_framework: str = ""   # GVR: which mathematical framework was used
    canonical_answer: int | None = None
    verification_confidence: str = ConfidenceLevel.UNVERIFIED.value
    verification_passed_checks: int = 0
    verification_failed_checks: int = 0
    verification_suspicious_checks: int = 0
    verification_summary: str = ""
    flaw_codes: list[str] = field(default_factory=list)
    flaw_severity_total: int = 0
    is_clean_trace: bool = True
    critique_summary: str = ""
    trace_confidence_score: float = 0.0  # DeepConf-style confidence


@dataclass
class ResearchTrace:
    """Full research trace for one problem -- the output artifact.

    Attributes:
        problem_id (str): The unique identifier for the problem.
        problem_text (str): The actual text of the math problem.
        source (str): The dataset source of the problem.
        difficulty (str): Categorical difficulty level.
        attempts (list[Attempt]): List of all reasoning attempts made.
        majority_vote_answers (dict): Tally of extracted answers during generation.
        final_answer (str | None): The agent's ultimately chosen answer.
        solved (bool): Indicates if the agent found a consensus/verified answer.
        total_duration_seconds (float): Total time spent researching the problem.
        total_attempts (int): Total number of reasoning attempts.
        strategy (str): The strategy used to arrive at the final answer.

    Note:
        Blindspot: The `solved` attribute being True does NOT mean the math is correct,
        it only means the model arrived at an answer that survived code execution
        and majority voting/self-correction loops.
    """
    problem_id: str
    problem_text: str
    source: str
    difficulty: str
    attempts: list[Attempt] = field(default_factory=list)
    majority_vote_answers: dict = field(default_factory=dict)
    final_answer: str | None = None
    solved: bool = False
    total_duration_seconds: float = 0.0
    total_attempts: int = 0
    strategy: str = ""  # "majority_vote" | "self_correct" | "exhausted"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AnswerGroup:
    """Attempts grouped by the same canonical answer for lean controller decisions."""
    answer: int
    attempts: list[Attempt]
    total_weight: float
    best_confidence: str        # ConfidenceLevel.value
    has_code_verified: bool
    has_clean_trace: bool
    flaw_summary: dict[str, int] = field(default_factory=dict)


# =============================================================================
# DeepResearcher v2
# =============================================================================

class DeepResearcher:
    """
    H100-optimized research agent for generating math reasoning traces.

    v2 implements:
    - Majority voting with N parallel samples
    - Tool-Integrated Reasoning (TIR)
    - Natural Language Verification
    - Dynamic time allocation
    - Auto model family detection
    """

    def __init__(
        self,
        model_path: str,
        time_limit_hours: float = 4.5,
        num_samples: int = 16,
        max_retries: int = 3,
        generate_temperature: float = 0.6,
        correct_temperature: float = 0.3,
        max_generate_tokens: int = 16384,
        max_correct_tokens: int = 4096,
        code_timeout: int = 30,
        gpu_memory_utilization: float = 0.95,
        max_model_len: int = 32768,
        patch_text: str | None = None,
        enable_tir: bool = True,
        enable_nl_verify: bool = True,
        tir_max_rounds: int = 3,
        dry_run: bool = False,
        submission_mode: bool = False,
    ):
        """Initialize the DeepResearcher v2.

        Args:
            model_path (str): Path to the AWQ-quantized model weights.
            time_limit_hours (float, optional): Hard time limit (default 4.5hr = 5hr - 30min buffer).
            num_samples (int, optional): Number of parallel samples for majority voting.
            max_retries (int, optional): Self-correction attempts for unresolved problems.
            generate_temperature (float, optional): Temperature for generation (creative).
            correct_temperature (float, optional): Temperature for corrections (precise).
            max_generate_tokens (int, optional): Max tokens per generation (8192 for long CoT).
            max_correct_tokens (int, optional): Max tokens per correction.
            code_timeout (int, optional): Timeout for sandboxed code execution (seconds).
            gpu_memory_utilization (float, optional): Fraction of GPU memory to use.
            max_model_len (int, optional): Maximum sequence length for the model.
            patch_text (str | None, optional): Optional System Prompt Patch from analysis.
            enable_tir (bool, optional): Enable Tool-Integrated Reasoning.
            enable_nl_verify (bool, optional): Enable Natural Language Verification.
            tir_max_rounds (int, optional): Max code execution rounds per TIR generation.
            dry_run (bool, optional): If True, skip vLLM init (for testing locally).
            submission_mode (bool, optional): If True, use lean wave-based controller
                instead of GVR for faster early stopping on easy problems.
        """
        self.model_path = model_path
        self.time_limit_hours = time_limit_hours
        self.time_limit_seconds = time_limit_hours * 3600
        self.num_samples = num_samples
        self.max_retries = max_retries
        self.generate_temperature = generate_temperature
        self.correct_temperature = correct_temperature
        self.max_generate_tokens = max_generate_tokens
        self.max_correct_tokens = max_correct_tokens
        self.code_timeout = code_timeout
        self.enable_tir = enable_tir
        self.enable_nl_verify = enable_nl_verify
        self.tir_max_rounds = tir_max_rounds
        self.dry_run = dry_run
        self.submission_mode = submission_mode
        self.start_time = None
        self._last_token_ids: list[int] = []  # Harmony channel parsing
        self._last_logprobs: list = []        # DeepConf confidence scoring
        self._batch_token_ids: list = []
        self._batch_logprobs: list = []
        self.verification_pipeline = VerificationPipeline()
        self.flaw_detector = FlawDetector()
        self.answer_selector = _answer_selector if _HAS_ANSWER_SELECTOR else None
        self.alpha_geometry_solver = AlphaGeometryRESolver()

        # Auto-detect model family for chat template
        self.model_family = detect_model_family(model_path)
        logger.info(f"Detected model family: {self.model_family}")

        # Build system prompt (with optional patches)
        self.system_prompt = build_system_prompt(patch_text)

        # Initialize vLLM engine via Harmony SDK
        self.harmony = None
        self.client = None
        self.encoding = None
        self.stop_token_ids = None
        if not dry_run:
            self._init_vllm(model_path, gpu_memory_utilization, max_model_len)
        else:
            self.llm = None
            self.tokenizer = None
            logger.info("DRY RUN mode -- vLLM not initialized")

    def _init_vllm(self, model_path: str, gpu_mem: float, max_len: int):
        """Initialize vLLM as HTTP server with Harmony SDK encoding.

        Uses HarmonyServer to start vLLM as an OpenAI-compatible HTTP server
        and load the Harmony encoding for gpt-oss. This is required because
        gpt-oss-120B was trained on Harmony format — without it, model output
        contains unparseable Harmony tokens.
        """
        logger.info("Loading model from %s", model_path)
        logger.info("  Model family:         %s", self.model_family)
        logger.info("  GPU memory util:      %.0f%%", gpu_mem * 100)
        logger.info("  Max model length:     %d", max_len)
        logger.info("  Majority vote N:      %d", self.num_samples)
        logger.info("  TIR enabled:          %s", self.enable_tir)
        logger.info("  NL Verify enabled:    %s", self.enable_nl_verify)

        self.harmony = HarmonyServer(
            model_path=model_path,
            gpu_memory_utilization=gpu_mem,
            max_model_len=max_len,
            served_model_name="gpt-oss",
            dry_run=self.dry_run,
        )

        self.client = self.harmony.client
        self.encoding = self.harmony.encoding
        self.stop_token_ids = self.harmony.stop_token_ids
        self.llm = None
        self.tokenizer = None

        logger.info("Model loaded successfully")

    # =========================================================================
    # Timer Management
    # =========================================================================

    def _check_timer(self):
        """Check if we have exceeded the time limit.

        Raises:
            TimeLimitExceeded: If the hard timer triggers a graceful exit.
        """
        if self.start_time is None:
            return
        elapsed = time.time() - self.start_time
        remaining = self.time_limit_seconds - elapsed
        if remaining <= 0:
            raise TimeLimitExceeded(
                f"Time limit of {self.time_limit_hours:.1f}hr exceeded "
                f"(elapsed: {elapsed / 3600:.2f}hr)"
            )

    def _remaining_seconds(self) -> float:
        """Get remaining seconds.

        Returns:
            float: The number of seconds left before the hard timer expires.
        """
        if self.start_time is None:
            return self.time_limit_seconds
        return max(0, self.time_limit_seconds - (time.time() - self.start_time))

    def _elapsed_str(self) -> str:
        """Human-readable elapsed time.

        Returns:
            str: Elapsed time formatted as "H:MM:SS".
        """
        if self.start_time is None:
            return "0:00:00"
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def _remaining_str(self) -> str:
        """Human-readable remaining time.

        Returns:
            str: Remaining time formatted as "H:MM".
        """
        remaining = self._remaining_seconds()
        if remaining <= 0:
            return "0:00:00"
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        return f"{hours}:{minutes:02d}"

    # =========================================================================
    # LLM Inference
    # =========================================================================

    def _build_harmony_conversation(self, user_prompt: str):
        """Build a Harmony Conversation from system + user prompts.

        Returns the Conversation object and the imported Harmony modules,
        or (None, None) if Harmony is not available.
        """
        from agent.harmony_layer import HARMONY_AVAILABLE
        if not HARMONY_AVAILABLE or self.encoding is None:
            return None, None

        from openai_harmony import (
            SystemContent, ReasoningEffort, Message, Role, Conversation,
        )

        system_content = (
            SystemContent.new()
            .with_model_identity(self.system_prompt)
            .with_reasoning_effort(reasoning_effort=ReasoningEffort.HIGH)
        )
        system_message = Message.from_role_and_content(Role.SYSTEM, system_content)
        user_message = Message.from_role_and_content(Role.USER, user_prompt)
        conversation = Conversation.from_messages([system_message, user_message])

        modules = {
            "Message": Message,
            "Role": Role,
            "Conversation": Conversation,
        }
        return conversation, modules

    def _decode_harmony_messages(self, token_ids: list[int]) -> str:
        """Decode Harmony token IDs into concatenated text from all message channels.

        Falls back to empty string if decoding fails or no text is found.
        """
        from openai_harmony import Role

        try:
            new_messages = self.encoding.parse_messages_from_completion_tokens(
                token_ids, Role.ASSISTANT
            )
        except Exception:
            return ""

        text_parts = []
        for msg in new_messages:
            if hasattr(msg, 'content') and msg.content:
                for content_item in msg.content:
                    if hasattr(content_item, 'text'):
                        text_parts.append(content_item.text)
        return '\n'.join(text_parts) if text_parts else ""

    def _generate_text(
        self,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate a single text response using Harmony-encoded OpenAI completions API.

        Encodes prompts via Harmony encoding, calls the vLLM HTTP server through
        the OpenAI completions API with token IDs, and decodes the response via
        Harmony parse_messages_from_completion_tokens.

        Args:
            user_prompt (str): The prompt to send to the model.
            temperature (float): The sampling temperature.
            max_tokens (int): The maximum number of tokens to generate.

        Returns:
            str: The generated text completion.
        """
        if self.dry_run:
            return (
                "[DRY RUN] This is a placeholder response.\n\n"
                "```python\nresult = 6 * 7\nprint(f'Result: {result}')\n```\n\n"
                "Let me verify by trying to disprove: 6*7 = 42 is well-known.\n"
                "**ANSWER: 42**"
            )

        from openai_harmony import Role

        # Build Harmony conversation (matching reference notebook pattern)
        conversation, _ = self._build_harmony_conversation(user_prompt)
        if conversation is None:
            raise RuntimeError("Harmony encoding required but not available")

        # Encode to token IDs
        prompt_ids = self.encoding.render_conversation_for_completion(
            conversation, Role.ASSISTANT
        )

        # Call OpenAI completions API (NOT chat -- completions with token IDs)
        response = self.client.completions.create(
            model="gpt-oss",
            temperature=temperature,
            logprobs=5,
            max_tokens=max_tokens,
            prompt=prompt_ids,
            seed=42,
            stream=False,
            extra_body={
                'min_p': 0.02,
                'stop_token_ids': self.stop_token_ids,
                'return_token_ids': True,
            }
        )

        choice = response.choices[0]

        # Store token IDs and logprobs for downstream DeepConf scoring
        self._last_token_ids = (
            list(choice.token_ids)
            if hasattr(choice, 'token_ids') and choice.token_ids
            else []
        )
        self._last_logprobs = []
        if choice.logprobs and hasattr(choice.logprobs, 'top_logprobs') and choice.logprobs.top_logprobs:
            self._last_logprobs = choice.logprobs.top_logprobs

        # Decode via Harmony to extract message channels
        if self._last_token_ids:
            decoded = self._decode_harmony_messages(self._last_token_ids)
            if decoded:
                return decoded
        return choice.text

    def _generate_batch(
        self,
        user_prompt: str,
        n: int,
        temperature: float,
        max_tokens: int,
    ) -> list[str]:
        """Generate N solutions using Harmony-encoded OpenAI completions API.

        Uses ThreadPoolExecutor for parallel completions with different seeds
        for sampling diversity. The vLLM HTTP server handles batching internally.

        Args:
            user_prompt (str): The prompt to send to the model.
            n (int): The number of parallel completions to generate.
            temperature (float): The sampling temperature.
            max_tokens (int): The maximum number of tokens to generate per completion.

        Returns:
            list[str]: A list of generated text completions.
        """
        if self.dry_run:
            return [self._generate_text(user_prompt, temperature, max_tokens)
                    for _ in range(min(n, 3))]  # Only 3 in dry run

        from openai_harmony import Role
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Build Harmony conversation once (same for all samples)
        conversation, _ = self._build_harmony_conversation(user_prompt)
        if conversation is None:
            raise RuntimeError("Harmony encoding required but not available")

        prompt_ids = self.encoding.render_conversation_for_completion(
            conversation, Role.ASSISTANT
        )

        self._batch_token_ids = [None] * n
        self._batch_logprobs = [None] * n

        def _single_completion(idx):
            attempt_seed = int((42 + idx) ** 2)
            response = self.client.completions.create(
                model="gpt-oss",
                temperature=temperature,
                logprobs=5,
                max_tokens=max_tokens,
                prompt=prompt_ids,
                seed=attempt_seed,
                stream=False,
                extra_body={
                    'min_p': 0.02,
                    'stop_token_ids': self.stop_token_ids,
                    'return_token_ids': True,
                }
            )
            choice = response.choices[0]
            token_ids = (
                list(choice.token_ids)
                if hasattr(choice, 'token_ids') and choice.token_ids
                else []
            )
            logprobs = (
                choice.logprobs.top_logprobs
                if choice.logprobs
                and hasattr(choice.logprobs, 'top_logprobs')
                and choice.logprobs.top_logprobs
                else []
            )

            # Decode via Harmony
            if token_ids:
                decoded = self._decode_harmony_messages(token_ids)
                text = decoded if decoded else choice.text
            else:
                text = choice.text

            self._batch_token_ids[idx] = token_ids
            self._batch_logprobs[idx] = logprobs
            return text

        # Run N completions in parallel (vLLM server handles batching)
        results = [None] * n
        with ThreadPoolExecutor(max_workers=min(n, 16)) as executor:
            futures = {executor.submit(_single_completion, i): i for i in range(n)}
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as exc:
                    logger.warning("Batch completion %d failed: %s", idx, exc)
                    results[idx] = ""

        return results

    # =========================================================================
    # Tool-Integrated Reasoning (TIR)
    # =========================================================================

    def _generate_with_tir(
        self,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate with Tool-Integrated Reasoning using Harmony conversation protocol.

        Uses the Harmony message channel protocol for structured multi-turn
        code execution. The model's output is decoded into typed messages:
        - 'analysis' channel: reasoning text
        - 'final' channel: the answer
        - recipient == 'python': code to execute

        This replaces the old text-matching approach (extract_code_blocks) with
        Harmony's structured message channels, matching the reference notebook
        (44-50) _process_attempt pattern.

        Args:
            user_prompt (str): The prompt to send to the model.
            temperature (float): The sampling temperature.
            max_tokens (int): The maximum number of tokens to generate overall.

        Returns:
            str: The final combined generation text including execution outputs.
        """
        if not self.enable_tir:
            return self._generate_text(user_prompt, temperature, max_tokens)

        if self.dry_run:
            return self._generate_text(user_prompt, temperature, max_tokens)

        from openai_harmony import Role, TextContent, Author, Message

        full_response = ""
        all_token_ids: list[int] = []
        all_logprobs: list = []

        # Build Harmony conversation
        conversation, _ = self._build_harmony_conversation(user_prompt)
        if conversation is None:
            raise RuntimeError("Harmony encoding required but not available")

        # Context limit for prompt+completion budget (matches max_model_len)
        context_limit = 32768

        for tir_round in range(self.tir_max_rounds + 1):
            # Encode conversation to token IDs
            prompt_ids = self.encoding.render_conversation_for_completion(
                conversation, Role.ASSISTANT
            )
            remaining_tokens = max_tokens - len(all_token_ids)
            call_max = min(remaining_tokens, context_limit - len(prompt_ids))

            if call_max < 100:
                break  # No token budget left

            # Stream completions via OpenAI API
            stream = self.client.completions.create(
                model="gpt-oss",
                temperature=temperature,
                logprobs=5,
                max_tokens=call_max,
                prompt=prompt_ids,
                seed=int((42 + tir_round) ** 2),
                stream=True,
                extra_body={
                    'min_p': 0.02,
                    'stop_token_ids': self.stop_token_ids,
                    'return_token_ids': True,
                }
            )

            token_buffer = []
            text_chunks = []
            try:
                for chunk in stream:
                    choice = chunk.choices[0]
                    new_tokens = (
                        choice.token_ids
                        if hasattr(choice, 'token_ids')
                        else None
                    )
                    new_text = choice.text or ""

                    if new_tokens:
                        token_buffer.extend(new_tokens)
                        all_token_ids.extend(new_tokens)
                        text_chunks.append(new_text)

                        # Collect logprobs for DeepConf
                        chunk_logprobs = choice.logprobs
                        if (
                            chunk_logprobs is not None
                            and hasattr(chunk_logprobs, 'top_logprobs')
                            and chunk_logprobs.top_logprobs
                        ):
                            all_logprobs.extend(chunk_logprobs.top_logprobs)
            finally:
                stream.close()

            if not token_buffer:
                break

            # Decode via Harmony -- extract structured messages
            try:
                new_messages = self.encoding.parse_messages_from_completion_tokens(
                    token_buffer, Role.ASSISTANT
                )
            except Exception as exc:
                # Fallback: treat raw stream text as the response
                logger.warning("Harmony decode failed: %s -- using raw text", exc)
                full_response += ''.join(text_chunks)
                break

            if not new_messages:
                # No structured messages decoded; use raw text
                full_response += ''.join(text_chunks)
                break

            conversation.messages.extend(new_messages)
            last_message = new_messages[-1]

            # Collect text for full_response accumulation
            for msg in new_messages:
                if hasattr(msg, 'content') and msg.content:
                    for content_item in msg.content:
                        if hasattr(content_item, 'text'):
                            full_response += content_item.text + "\n"

            # Check: final answer channel
            if hasattr(last_message, 'channel') and last_message.channel == 'final':
                # The final channel contains the answer
                if hasattr(last_message, 'content') and last_message.content:
                    for content_item in last_message.content:
                        if hasattr(content_item, 'text'):
                            full_response += content_item.text
                break

            # Check: tool use (code execution request via Harmony protocol)
            if (
                hasattr(last_message, 'recipient')
                and last_message.recipient == 'python'
            ):
                # Extract code from the tool-use message
                code_text = ""
                if hasattr(last_message, 'content') and last_message.content:
                    for content_item in last_message.content:
                        if hasattr(content_item, 'text'):
                            code_text += content_item.text

                if code_text.strip():
                    # Execute via our existing sandbox
                    passed, exec_output = run_verification(
                        f"```python\n{code_text}\n```",
                        timeout=self.code_timeout,
                    )
                    exec_output = exec_output[:2000]  # Cap output length

                    full_response += (
                        f"\n[Code execution: {'PASS' if passed else 'FAIL'}]\n"
                        f"{exec_output}\n"
                    )

                    # Build tool response as Harmony Message
                    # (matches reference notebook _make_response pattern)
                    tool_content = TextContent(text=exec_output)
                    tool_author = Author(role=Role.TOOL, name='python')
                    tool_response = Message(
                        author=tool_author, content=[tool_content]
                    ).with_recipient('assistant')

                    # Preserve the channel from the request if present
                    if (
                        hasattr(last_message, 'channel')
                        and last_message.channel
                    ):
                        tool_response = tool_response.with_channel(
                            last_message.channel
                        )

                    conversation.messages.append(tool_response)

                    logger.info(
                        "    TIR round %d: %s | Output: %s...",
                        tir_round + 1,
                        'PASS' if passed else 'FAIL',
                        exec_output[:80],
                    )
                continue

            # Early pruning: if confidence drops below threshold, abort trace.
            # This saves 43-85% of tokens on low-quality traces (DeepConf).
            # Only prune after substantial generation (>1024 tokens) to avoid
            # killing traces that start uncertain but recover.
            if (
                _HAS_CONFIDENCE_SCORER
                and len(all_logprobs) > 1024
                and hasattr(self, '_confidence_threshold')
                and self._confidence_threshold > 0
            ):
                recent_logprobs = all_logprobs[-512:]
                from src.solver.confidence_scorer import compute_token_confidences
                recent_confs = compute_token_confidences(recent_logprobs)
                if recent_confs:
                    recent_mean = sum(recent_confs) / len(recent_confs)
                    if recent_mean > self._confidence_threshold * 1.5:
                        logger.info(
                            "    [Prune] Aborting trace at %d tokens "
                            "(conf=%.2f > threshold=%.2f)",
                            len(all_token_ids),
                            recent_mean,
                            self._confidence_threshold,
                        )
                        break

        # Store accumulated token_ids and logprobs for downstream use
        self._last_token_ids = all_token_ids
        self._last_logprobs = all_logprobs
        return full_response

    # =========================================================================
    # Live Verification Integration
    # =========================================================================

    def _confidence_from_value(self, value: str) -> ConfidenceLevel:
        """Parse a stored confidence string back into the enum."""
        try:
            return ConfidenceLevel(value)
        except ValueError:
            return ConfidenceLevel.UNVERIFIED

    def _cap_confidence(
        self,
        confidence: ConfidenceLevel,
        ceiling: ConfidenceLevel,
    ) -> ConfidenceLevel:
        """Clamp confidence to a weaker ceiling when flaws undermine trust."""
        if confidence.strength > ceiling.strength:
            return ceiling
        return confidence

    def _annotated_solution(self, attempt: Attempt) -> AnnotatedSolution | None:
        """Convert a runtime Attempt into the typed selector input."""
        if not _HAS_ANSWER_SELECTOR or self.answer_selector is None:
            return None
        return AnnotatedSolution(
            final_answer=attempt.canonical_answer,
            report=VerificationReport(
                passed_checks=attempt.verification_passed_checks,
                failed_checks=attempt.verification_failed_checks,
                suspicious_checks=attempt.verification_suspicious_checks,
                confidence=self._confidence_from_value(attempt.verification_confidence),
            ),
            attempt_id=attempt.attempt_number,
            raw_text=attempt.solution_text,
            flaw_severity_total=attempt.flaw_severity_total,
            is_clean_trace=attempt.is_clean_trace,
            flaw_codes=tuple(attempt.flaw_codes),
        )

    def _attempt_vote_weight(self, attempt: Attempt) -> float:
        """Return the selector weight for one attempt.

        Combines verification-based weight with DeepConf confidence:
          weight = verification_weight * max(trace_confidence, 0.1)
        The floor of 0.1 prevents zero-confidence traces from being
        completely silenced — they still participate in voting but weakly.
        """
        annotated = self._annotated_solution(attempt)
        if annotated is None or self.answer_selector is None:
            base = 1.0 if attempt.canonical_answer is not None else 0.0
        else:
            base = self.answer_selector.vote_weight(annotated)
        # Multiply by trace confidence if available
        if attempt.trace_confidence_score > 0:
            base *= max(attempt.trace_confidence_score, 0.1)
        return base

    def _score_answers(self, attempts: list[Attempt]) -> dict[str, float]:
        """Aggregate selector scores by answer string for logging and consensus."""
        if _HAS_ANSWER_SELECTOR and self.answer_selector is not None:
            annotated = [
                ann for att in attempts
                if (ann := self._annotated_solution(att)) is not None
            ]
            scores = self.answer_selector.score_answers(annotated)
            return {str(answer): round(score, 4) for answer, score in scores.items()}

        scores: Counter = Counter()
        for attempt in attempts:
            if attempt.extracted_answer is not None:
                scores[attempt.extracted_answer] += 1
        return dict(scores)

    def _select_answer_from_attempts(
        self,
        attempts: list[Attempt],
    ) -> tuple[str | None, str, float, dict[str, float]]:
        """Select the best answer from runtime attempts using typed evidence."""
        vote_dict = self._score_answers(attempts)
        if _HAS_ANSWER_SELECTOR and self.answer_selector is not None:
            annotated = [
                ann for att in attempts
                if (ann := self._annotated_solution(att)) is not None
            ]
            selected, reason, confidence = self.answer_selector.select(annotated)
            return (
                str(selected) if selected is not None else None,
                reason,
                confidence,
                vote_dict,
            )

        if not vote_dict:
            return None, "no_answer_extracted", 0.0, {}
        answer, score = max(vote_dict.items(), key=lambda item: item[1])
        total = sum(vote_dict.values()) or 1.0
        return answer, "fallback_weighted_vote", score / total, vote_dict

    def _best_attempt(self, attempts: list[Attempt]) -> Attempt | None:
        """Pick the strongest single attempt using typed confidence + flaw penalties."""
        candidates = [a for a in attempts if a.canonical_answer is not None]
        if not candidates:
            candidates = list(attempts)
        if not candidates:
            return None
        return max(
            candidates,
            key=lambda a: (
                self._attempt_vote_weight(a),
                a.canonical_answer is not None,
                a.is_clean_trace,
                a.verification_passed,
            ),
        )

    def _best_attempt_for_answer(
        self,
        attempts: list[Attempt],
        answer: str | None,
    ) -> Attempt | None:
        """Pick the best attempt supporting a specific answer."""
        if answer is None:
            return None
        candidates = [a for a in attempts if a.extracted_answer == answer]
        if not candidates:
            return None
        return self._best_attempt(candidates)

    def _attempt_is_acceptable(self, attempt: Attempt | None) -> bool:
        """Require both typed evidence and acceptable trace quality."""
        if attempt is None or attempt.canonical_answer is None:
            return False

        blocking_flaws = {
            FlawCode.NON_EXECUTABLE_CODE,
            FlawCode.MALFORMED_TOOL_CALL,
            FlawCode.PROMPT_LEAKAGE,
            FlawCode.CONTEXT_CONFABULATION,
            FlawCode.FALSE_STATUS,
        }
        if set(attempt.flaw_codes) & blocking_flaws:
            return False
        if attempt.verification_failed_checks > 0:
            return False

        confidence = self._confidence_from_value(attempt.verification_confidence)
        if confidence.strength >= ConfidenceLevel.ENUMERATED.strength:
            return True

        return (
            confidence == ConfidenceLevel.NL_JUDGMENT
            and attempt.is_clean_trace
            and attempt.verification_passed
        )

    # =========================================================================
    # Lean Controller Helpers
    # =========================================================================

    def _attempt_is_acceptable_lean(self, attempt: Attempt | None) -> bool:
        """Relaxed acceptance for submission mode: only hard blockers reject."""
        if attempt is None or attempt.canonical_answer is None:
            return False
        if attempt.verification_failed_checks > 0:
            return False
        if FlawCode.FALSE_STATUS in attempt.flaw_codes:
            return False
        return True

    def _build_answer_groups(self, attempts: list[Attempt]) -> list[AnswerGroup]:
        """Group attempts by canonical answer, compute per-group metrics."""
        groups: dict[int, list[Attempt]] = {}
        for att in attempts:
            if att.canonical_answer is not None:
                groups.setdefault(att.canonical_answer, []).append(att)

        result = []
        for answer, group_attempts in groups.items():
            total_weight = sum(
                self._attempt_vote_weight(a) for a in group_attempts
            )
            best_conf = max(
                (
                    self._confidence_from_value(a.verification_confidence)
                    for a in group_attempts
                ),
                key=lambda c: c.strength,
            )
            has_code = any(a.verification_passed for a in group_attempts)
            has_clean = any(a.is_clean_trace for a in group_attempts)
            flaw_summary: dict[str, int] = {}
            for a in group_attempts:
                for fc in a.flaw_codes:
                    flaw_summary[fc] = flaw_summary.get(fc, 0) + 1

            result.append(AnswerGroup(
                answer=answer,
                attempts=group_attempts,
                total_weight=total_weight,
                best_confidence=best_conf.value,
                has_code_verified=has_code,
                has_clean_trace=has_clean,
                flaw_summary=flaw_summary,
            ))

        result.sort(key=lambda g: g.total_weight, reverse=True)
        return result

    def _is_submit_safe(
        self,
        groups: list[AnswerGroup],
        total_attempts: int,
        min_support: int = 3,
        min_share: float = 0.50,
    ) -> tuple[bool, str]:
        """Check if the leading answer group is safe to submit.

        Returns (is_safe, reason_string). Only hard contradictions block;
        hygiene flaws (CHANNEL_LEAKAGE, CONTEXT_CONFABULATION, etc.) do not.
        """
        if not groups:
            return False, "no_groups"

        leader = groups[0]
        total_weight = sum(g.total_weight for g in groups)
        share = leader.total_weight / total_weight if total_weight > 0 else 0
        support = len(leader.attempts)

        # Hard blockers at answer-group level
        has_hard_contradiction = any(
            a.verification_failed_checks > 0 for a in leader.attempts
        )
        if has_hard_contradiction:
            return False, "hard_contradiction"

        if any(FlawCode.FALSE_STATUS in a.flaw_codes for a in leader.attempts):
            return False, "false_status"

        if support >= min_support and share >= min_share:
            return True, f"consensus_{support}_{share:.0%}"

        return False, f"insufficient_{support}_{share:.0%}"

    def _build_attempt_feedback(self, attempt: Attempt | None) -> str:
        """Convert verifier/flaw findings into actionable correction feedback."""
        if attempt is None:
            return (
                "Your previous solution did not yield a trusted final answer. "
                "Produce a mechanically checkable solution and end with **ANSWER: [value]**."
            )

        hints: list[str] = []
        flaw_hints = {
            FlawCode.MISSING_FINAL_COMMIT:
                "State the final value explicitly as **ANSWER: [integer]**.",
            FlawCode.CHANNEL_LEAKAGE:
                "Do not leak internal channel tokens like 'analysis' into the answer.",
            FlawCode.MALFORMED_TOOL_CALL:
                "Use standard fenced Python code blocks instead of assistantcommentary syntax.",
            FlawCode.PSEUDO_VERIFICATION:
                "Make the code print the exact numeric value that proves the final answer.",
            FlawCode.NON_EXECUTABLE_CODE:
                "Fix the Python block so it executes cleanly end-to-end.",
            FlawCode.CONTEXT_CONFABULATION:
                "Solve using only the information in the problem statement; do not ask for prior context.",
            FlawCode.PROMPT_LEAKAGE:
                "Do not copy user instructions into the final reasoning trace.",
        }
        for flaw_code in attempt.flaw_codes:
            hint = flaw_hints.get(flaw_code)
            if hint and hint not in hints:
                hints.append(hint)

        if attempt.canonical_answer is None:
            hints.append("No canonical integer answer was extracted from the trace.")
        if attempt.verification_summary:
            hints.append(f"Verification summary: {attempt.verification_summary}")
        if attempt.verification_output.strip():
            hints.append(
                "Verification output:\n"
                + attempt.verification_output[:1200]
            )

        return "\n\n".join(hints) if hints else (
            "Strengthen the proof with executable checks and finish with **ANSWER: [value]**."
        )

    def _build_live_report(
        self,
        pipe_result,
        verification_passed: bool,
        verification_output: str,
        code_blocks_found: int,
        critique,
        canonical_answer: int | None,
    ) -> VerificationReport:
        """Merge pipeline checks, sandbox execution, and flaw detection."""
        breakdown = {
            level: dict(counts)
            for level, counts in pipe_result.report.breakdown.items()
        }
        passed = pipe_result.report.passed_checks
        failed = pipe_result.report.failed_checks
        suspicious = pipe_result.report.suspicious_checks

        answer_text = str(canonical_answer) if canonical_answer is not None else None
        answer_in_output = False
        if answer_text:
            answer_in_output = (
                re.search(rf"(?<!\d){re.escape(answer_text)}(?!\d)", verification_output)
                is not None
            )

        arithmetic_pass = any(
            check.status == VerificationStatus.PASS
            for check in pipe_result.arithmetic_results
        )
        arithmetic_fail = any(
            check.status == VerificationStatus.FAIL
            for check in pipe_result.arithmetic_results
        )
        answer_format_pass = (
            pipe_result.answer_format is not None
            and pipe_result.answer_format.status == VerificationStatus.PASS
        )

        exec_confidence = ConfidenceLevel.UNVERIFIED
        if (
            verification_passed
            and code_blocks_found > 0
            and answer_text
            and answer_in_output
        ):
            exec_confidence = ConfidenceLevel.LEVEL_0_EXACT
        elif verification_passed and code_blocks_found > 0 and answer_text:
            exec_confidence = ConfidenceLevel.ENUMERATED
        elif code_blocks_found > 0 and not verification_passed:
            suspicious += 1
            breakdown.setdefault(
                ConfidenceLevel.UNVERIFIED.value,
                {"pass": 0, "fail": 0, "suspicious": 0},
            )
            breakdown[ConfidenceLevel.UNVERIFIED.value]["suspicious"] += 1

        if exec_confidence != ConfidenceLevel.UNVERIFIED:
            passed += 1
            breakdown.setdefault(
                exec_confidence.value,
                {"pass": 0, "fail": 0, "suspicious": 0},
            )
            breakdown[exec_confidence.value]["pass"] += 1

        confidence = ConfidenceLevel.UNVERIFIED
        if arithmetic_pass and not arithmetic_fail:
            confidence = ConfidenceLevel.LEVEL_0_EXACT
        elif exec_confidence != ConfidenceLevel.UNVERIFIED:
            confidence = exec_confidence
        elif answer_format_pass and answer_text:
            # Format-only success means we found a plausible answer, not
            # that we mechanically proved it.
            confidence = ConfidenceLevel.NL_JUDGMENT

        critical_flaws = {
            FlawCode.NON_EXECUTABLE_CODE,
            FlawCode.MALFORMED_TOOL_CALL,
            FlawCode.PROMPT_LEAKAGE,
            FlawCode.CONTEXT_CONFABULATION,
        }
        major_flaws = critical_flaws | {
            FlawCode.PSEUDO_VERIFICATION,
            FlawCode.CHANNEL_LEAKAGE,
            FlawCode.MISSING_FINAL_COMMIT,
        }
        flaw_codes = set(critique.flaw_codes)

        if flaw_codes & critical_flaws:
            confidence = ConfidenceLevel.UNVERIFIED
            suspicious += 1
            breakdown.setdefault(
                ConfidenceLevel.UNVERIFIED.value,
                {"pass": 0, "fail": 0, "suspicious": 0},
            )
            breakdown[ConfidenceLevel.UNVERIFIED.value]["suspicious"] += 1
        elif flaw_codes & major_flaws:
            confidence = self._cap_confidence(confidence, ConfidenceLevel.NL_JUDGMENT)
            suspicious += 1
            breakdown.setdefault(
                ConfidenceLevel.NL_JUDGMENT.value,
                {"pass": 0, "fail": 0, "suspicious": 0},
            )
            breakdown[ConfidenceLevel.NL_JUDGMENT.value]["suspicious"] += 1

        return VerificationReport(
            passed_checks=passed,
            failed_checks=failed,
            suspicious_checks=suspicious,
            confidence=confidence,
            breakdown=breakdown,
        )

    def _analyze_completed_solution(
        self,
        solution: str,
        attempt_number: int,
        duration_seconds: float,
        approach_framework: str = "",
        token_ids: list[int] | None = None,
        logprobs: list | None = None,
    ) -> Attempt:
        """Run the live verification stack on a finished solution attempt."""
        if self.dry_run:
            canonical_answer = 42
            critique = self.flaw_detector.detect_all(solution, "")
            return Attempt(
                attempt_number=attempt_number,
                solution_text=solution,
                extracted_answer=str(canonical_answer),
                code_blocks_found=1,
                verification_passed=True,
                verification_output="[DRY RUN] synthetic verification passed",
                duration_seconds=duration_seconds,
                approach_framework=approach_framework,
                canonical_answer=canonical_answer,
                verification_confidence=ConfidenceLevel.ENUMERATED.value,
                verification_passed_checks=1,
                verification_failed_checks=0,
                verification_suspicious_checks=0,
                verification_summary="ENUMERATED (pass=1, fail=0, suspicious=0)",
                flaw_codes=sorted(critique.flaw_codes),
                flaw_severity_total=critique.severity_total,
                is_clean_trace=critique.is_clean,
                critique_summary=critique.summary(),
                trace_confidence_score=0.0,
            )

        code_blocks = extract_code_blocks(solution)
        verification_passed, verification_output = run_verification(
            solution,
            timeout=self.code_timeout,
        )

        trace = SolutionTrace(raw_text=solution)
        pipe_result = self.verification_pipeline.run(trace)
        canonical_answer = pipe_result.final_answer

        if canonical_answer is None:
            fallback_answer = extract_answer(solution, token_ids=token_ids)
            if fallback_answer is not None and fallback_answer.isdigit():
                canonical_answer = int(fallback_answer)

        critique = self.flaw_detector.detect_all(solution, verification_output)
        report = self._build_live_report(
            pipe_result=pipe_result,
            verification_passed=verification_passed,
            verification_output=verification_output,
            code_blocks_found=len(code_blocks),
            critique=critique,
            canonical_answer=canonical_answer,
        )

        # DeepConf-style confidence scoring from logprobs
        trace_conf_score = 0.0
        if _HAS_CONFIDENCE_SCORER and logprobs:
            trace_conf = score_trace(logprobs)
            trace_conf_score = trace_conf.score

        extracted_answer = str(canonical_answer) if canonical_answer is not None else None
        verification_summary = (
            f"{report.confidence.value} "
            f"(pass={report.passed_checks}, fail={report.failed_checks}, "
            f"suspicious={report.suspicious_checks})"
        )

        return Attempt(
            attempt_number=attempt_number,
            solution_text=solution,
            extracted_answer=extracted_answer,
            code_blocks_found=len(code_blocks),
            verification_passed=verification_passed,
            verification_output=verification_output,
            duration_seconds=duration_seconds,
            approach_framework=approach_framework,
            canonical_answer=canonical_answer,
            verification_confidence=report.confidence.value,
            verification_passed_checks=report.passed_checks,
            verification_failed_checks=report.failed_checks,
            verification_suspicious_checks=report.suspicious_checks,
            verification_summary=verification_summary,
            flaw_codes=sorted(critique.flaw_codes),
            flaw_severity_total=critique.severity_total,
            is_clean_trace=critique.is_clean,
            critique_summary=critique.summary(),
            trace_confidence_score=trace_conf_score,
        )

    # =========================================================================
    # Geometry Backends
    # =========================================================================

    def _maybe_run_geometry_backend(
        self,
        problem: dict,
        problem_text: str,
        topic: str | None,
    ) -> str:
        """Augment geometry problems with AlphaGeometryRE proof context when possible."""
        if topic != "geometry" or not self.alpha_geometry_solver.is_available():
            return problem_text

        formal_problem = (
            problem.get("formal_geometry_problem")
            or problem.get("alpha_geometry_problem")
            or extract_formal_geometry_problem(problem_text)
        )

        if formal_problem is None and not self.dry_run:
            formalization_prompt = build_alpha_geometry_formalization_prompt(problem_text)
            candidate = self._generate_text(
                formalization_prompt,
                temperature=0.1,
                max_tokens=768,
            )
            formal_problem = extract_formal_geometry_problem(candidate)

        if formal_problem is None:
            logger.info("    [Geometry] No AlphaGeometryRE formalization available.")
            return problem_text

        try:
            result = self.alpha_geometry_solver.solve(
                formal_problem=formal_problem,
                problem_name=problem.get("id", "geometry_problem"),
                mode=problem.get("alpha_geometry_mode", "ddar"),
                timeout=max(60, self.code_timeout * 3),
                beam_size=int(problem.get("alpha_geometry_beam_size", 2)),
                search_depth=int(problem.get("alpha_geometry_search_depth", 2)),
                batch_size=int(problem.get("alpha_geometry_batch_size", 2)),
            )
        except Exception as exc:
            logger.info(f"    [Geometry] AlphaGeometryRE invocation failed: {exc}")
            return problem_text

        if not result.proved:
            logger.info(
                f"    [Geometry] AlphaGeometryRE did not prove the goal "
                f"({result.summary})."
            )
            return problem_text

        proof_excerpt = (result.proof_text or result.stdout)[-3000:]
        logger.info(f"    [Geometry] AlphaGeometryRE proved the formal goal ({result.summary}).")
        return (
            f"{problem_text}\n\n"
            "[AlphaGeometryRE backend]\n"
            f"Formalization:\n{formal_problem}\n\n"
            "Trusted proof trace (use these geometric relations as auxiliary facts, "
            "then still compute the final numeric answer independently):\n"
            f"{proof_excerpt}"
        )

    # =========================================================================
    # Natural Language Verification
    # =========================================================================

    def _nl_verify(self, problem_text: str, solution: str) -> tuple[bool, str]:
        """Run natural language verification on a solution.

        Args:
            problem_text (str): The problem being solved.
            solution (str): The model's proposed solution.

        Returns:
            tuple[bool, str]: Success boolean and verdict message.

        Note:
            Bug/Blindspot: The NL verifier uses the exact same model to review its own output,
            which often leads to a rubber-stamp confirmation bias.
        """
        if not self.enable_nl_verify:
            return True, "NL Verify disabled"

        nl_prompt = build_nl_verify_prompt(problem_text, solution)
        nl_response = self._generate_text(
            nl_prompt,
            temperature=0.2,  # Low temperature for careful review
            max_tokens=1024,
        )
        return extract_nl_verdict(nl_response)

    # =========================================================================
    # Majority Voting (with Early Stopping)
    # =========================================================================

    def _check_early_consensus(
        self,
        answer_counts: Counter,
        total_generated: int,
    ) -> str | None:
        """Check if we have early consensus to stop generating more samples.

        Thresholds (from NemoSkills 1st place):
          - With 4 samples: need 3/4 (75%) agreement
          - With 8 samples: need 5/8 (63%) agreement
          - With 12+ samples: need 7/12 (58%) agreement

        Args:
            answer_counts (Counter): Tally of extracted answers so far.
            total_generated (int): Total number of samples generated so far.

        Returns:
            str | None: The consensus answer string if thresholds are met, else None.
        """
        if not answer_counts:
            return None

        top_answer, top_count = answer_counts.most_common(1)[0]
        total_votes = sum(answer_counts.values())

        # Scale threshold: stricter with fewer samples
        if total_generated <= 4:
            threshold = 0.75  # 3/4 must agree
        elif total_generated <= 8:
            threshold = 0.63  # 5/8 must agree
        else:
            threshold = 0.58  # 7/12 must agree

        consensus_ratio = top_count / total_votes
        if consensus_ratio >= threshold:
            logger.info(
                f"    ⚡ Early consensus after {total_generated} samples: "
                f"'{top_answer}' at {consensus_ratio:.0%} (threshold: {threshold:.0%})"
            )
            return top_answer

        return None

    def _majority_vote(
        self,
        problem: dict,
    ) -> tuple[list[Attempt], dict, str | None]:
        """Generate N solutions in waves with early stopping on consensus.

        Wave strategy (inspired by NemoSkills 1st place):
          - Wave 1: Generate 4 → check consensus (saves 75% compute if strong)
          - Wave 2: Generate 4 more (total 8) → check consensus (saves 50%)
          - Wave 3: Generate 4 more (total 12) → check consensus (saves 25%)
          - Wave 4: Generate remaining to reach num_samples → final vote

        Args:
            problem (dict): The problem dictionary containing `problem_text`.

        Returns:
            tuple[list[Attempt], dict, str | None]: A tuple containing the list of attempts,
                                                    the vote dictionary, and the consensus answer (if any).
        """
        problem_text = problem["problem_text"]
        generate_prompt = build_generate_prompt(problem_text)
        # Adaptive compute: start with a base budget, escalate for hard problems.
        # TIR mode caps lower because each generation is sequential (slower).
        base_n = min(self.num_samples, 8) if self.enable_tir else self.num_samples
        max_n = min(self.num_samples * 2, 32)  # Hard cap for escalation
        effective_n = base_n
        wave_size = 4
        escalated = False

        logger.info(
            f"    Generating up to {effective_n} samples "
            f"(wave_size={wave_size}, early_stop=on, max_escalation={max_n})..."
        )

        batch_start = time.time()
        all_solutions = []
        attempts = []
        answer_counts = Counter()
        early_stopped = False
        consensus = None

        # Generate in waves
        generated = 0
        while generated < effective_n:
            self._check_timer()
            wave_n = min(wave_size, effective_n - generated)

            if self.enable_tir:
                # TIR: generate one at a time within the wave
                wave_solutions = []
                wave_token_ids: list[list[int] | None] = []
                wave_logprobs: list[list | None] = []
                for _ in range(wave_n):
                    self._check_timer()
                    sol = self._generate_with_tir(
                        generate_prompt,
                        temperature=self.generate_temperature,
                        max_tokens=self.max_generate_tokens,
                    )
                    wave_solutions.append(sol)
                    wave_token_ids.append(getattr(self, '_last_token_ids', None))
                    wave_logprobs.append(getattr(self, '_last_logprobs', None))
            else:
                # Batch: generate wave_n at once
                wave_solutions = self._generate_batch(
                    generate_prompt,
                    n=wave_n,
                    temperature=self.generate_temperature,
                    max_tokens=self.max_generate_tokens,
                )
                wave_token_ids = getattr(self, '_batch_token_ids', [None] * len(wave_solutions))
                wave_logprobs = getattr(self, '_batch_logprobs', [None] * len(wave_solutions))

            # Process wave results
            wave_duration = (time.time() - batch_start) / max(generated + len(wave_solutions), 1)
            for i, solution in enumerate(wave_solutions):
                tids = wave_token_ids[i] if i < len(wave_token_ids) else None
                lprobs = wave_logprobs[i] if i < len(wave_logprobs) else None
                attempt = self._analyze_completed_solution(
                    solution=solution,
                    attempt_number=generated + i + 1,
                    duration_seconds=wave_duration,
                    token_ids=tids,
                    logprobs=lprobs,
                )
                attempts.append(attempt)

                if attempt.extracted_answer is not None:
                    answer_counts[attempt.extracted_answer] += self._attempt_vote_weight(attempt)

            generated += len(wave_solutions)
            all_solutions.extend(wave_solutions)

            # Calibrate confidence threshold from first wave (DeepConf warmup).
            # Set threshold at the 10th percentile of min-group-confidence
            # across warmup traces. Subsequent traces with confidence below
            # this are pruned early in _generate_with_tir.
            if (
                generated == wave_size
                and _HAS_CONFIDENCE_SCORER
                and not hasattr(self, '_confidence_threshold')
            ):
                conf_scores = [
                    a.trace_confidence_score for a in attempts
                    if a.trace_confidence_score > 0
                ]
                if conf_scores:
                    # 90th percentile of confidence = threshold for pruning
                    # (higher confidence value = less certain, so prune above this)
                    sorted_confs = sorted(conf_scores)
                    p90_idx = min(len(sorted_confs) - 1, int(len(sorted_confs) * 0.9))
                    self._confidence_threshold = sorted_confs[p90_idx]
                    logger.info(
                        f"    [DeepConf] Calibrated pruning threshold: "
                        f"{self._confidence_threshold:.2f} "
                        f"(from {len(conf_scores)} warmup traces)"
                    )
                else:
                    self._confidence_threshold = 0  # Disable pruning

            # Check for early consensus (don't check on last wave)
            if generated < effective_n:
                early_answer = self._check_early_consensus(answer_counts, generated)
                if early_answer is not None:
                    consensus = early_answer
                    early_stopped = True
                    break

            # Adaptive escalation: after initial waves, if consensus is weak
            # and we have time budget remaining, generate more samples.
            # This concentrates compute on hard problems (disagreement = hard).
            problem_time_left = (
                getattr(self, '_problem_deadline', float('inf')) - time.time()
            )
            if (
                generated >= base_n
                and not escalated
                and consensus is None
                and self._remaining_seconds() > 120  # At least 2 min global
                and problem_time_left > 60  # At least 1 min on this problem
            ):
                # Check how weak the current vote is
                if answer_counts:
                    top_count = answer_counts.most_common(1)[0][1]
                    total_votes = sum(answer_counts.values())
                    ratio = top_count / total_votes if total_votes > 0 else 0
                else:
                    ratio = 0

                # Also check average trace confidence
                avg_conf = 0.0
                conf_attempts = [a for a in attempts if a.trace_confidence_score > 0]
                if conf_attempts:
                    avg_conf = sum(a.trace_confidence_score for a in conf_attempts) / len(conf_attempts)

                # Escalate if: weak consensus (<50%) OR low avg confidence
                if ratio < 0.50 or (avg_conf > 0 and avg_conf > 4.0):
                    old_n = effective_n
                    effective_n = min(max_n, effective_n + wave_size * 2)
                    escalated = True
                    logger.info(
                        f"    [Adaptive] Escalating: {old_n} → {effective_n} samples "
                        f"(consensus={ratio:.0%}, avg_conf={avg_conf:.2f})"
                    )

        batch_duration = time.time() - batch_start
        saved_pct = max(0, (base_n - generated) / base_n * 100) if early_stopped else 0
        escalation_note = f", escalated to {effective_n}" if escalated else ""
        logger.info(
            f"    Generation: {generated}/{effective_n} solutions in {batch_duration:.1f}s"
            f"{f' (saved {saved_pct:.0f}% via early stop)' if early_stopped else ''}"
            f"{escalation_note}"
        )

        # Final consensus if not already found via early stopping
        if consensus is None:
            vote_dict = dict(answer_counts)
            if answer_counts:
                top_answer, top_count = answer_counts.most_common(1)[0]
                total_votes = sum(answer_counts.values())
                consensus_ratio = top_count / total_votes
                logger.info(
                    f"    Majority vote: '{top_answer}' with {top_count}/{total_votes} "
                    f"votes ({consensus_ratio:.0%})"
                )
                if consensus_ratio >= 0.3:  # Accept if ≥30% agreement (weighted)
                    consensus = top_answer
        else:
            vote_dict = dict(answer_counts)

        return attempts, vote_dict, consensus

    # =========================================================================
    # GenSelect (Generative Solution Selection)
    # =========================================================================

    def _genselect(
        self,
        problem: dict,
        attempts: list,
    ) -> str | None:
        """Use the model to select the best solution via comparative evaluation.

        Inspired by NemoSkills (AIMO2 1st place): when majority vote has
        weak consensus, feeding all solution summaries back into the model
        and asking it to pick the best one can recover +3-5% accuracy.

        Args:
            problem (dict): The problem dictionary.
            attempts (list[Attempt]): The list of previous attempts to evaluate.

        Returns:
            str | None: The selected answer string, or None if selection fails.

        Note:
            Blindspot: GenSelect arbitrarily truncates solution summaries to ~500 tokens.
            If the critical logical flaw (or correct step) is buried deeper in the reasoning,
            the GenSelect model will make a blind choice based on truncated data.
        """
        # Only consider attempts that have an extracted answer
        valid = [a for a in attempts if a.extracted_answer is not None]
        if len(valid) < 2:
            return None

        # Build solution summaries (truncated to fit context)
        summaries = []
        max_per_summary = 2000  # ~500 tokens each
        for i, att in enumerate(valid):
            verified = "✓ code verified" if att.verification_passed else "✗ unverified"
            summary = att.solution_text[:max_per_summary]
            summaries.append(
                f"## Solution {i + 1} (Answer: {att.extracted_answer}, {verified})\n"
                f"{summary}"
            )

        summary_block = "\n---\n".join(summaries)
        genselect_prompt = (
            f"You are evaluating {len(valid)} candidate solutions to this problem:\n\n"
            f"{problem['problem_text']}\n\n"
            f"{summary_block}\n\n"
            f"## Task\n"
            f"Analyze each solution's reasoning quality. Identify which has:\n"
            f"1. The most rigorous mathematical reasoning\n"
            f"2. Correct intermediate steps verified by code\n"
            f"3. No logical gaps or unproven assumptions\n\n"
            f"Output ONLY the number of the best solution: BEST: [number]"
        )

        logger.info(f"    GenSelect: evaluating {len(valid)} candidates...")

        response = self._generate_text(
            genselect_prompt,
            temperature=0.1,  # Low temp for careful evaluation
            max_tokens=2048,
        )

        # Extract selection
        match = re.search(r"BEST:\s*(\d+)", response)
        if match:
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(valid):
                selected = valid[idx].extracted_answer
                logger.info(f"    GenSelect chose Solution {idx + 1}: '{selected}'")
                return selected

        logger.info("    GenSelect failed to extract a valid selection")
        return None

    # =========================================================================
    # Approach-Diverse GVR (Generator → Verifier → Reviser)
    # =========================================================================

    def _generate_approach_diverse(
        self,
        problem: dict,
    ) -> tuple[list[Attempt], dict, str | None]:
        """Generate solutions using 4 semantically distinct mathematical frameworks.

        Instead of temperature-diverse majority vote (correlated errors), each
        solution uses a fundamentally different reasoning strategy: algebraic,
        computational, case-analysis, or number-theoretic.

        When 2+ independent frameworks agree on the same answer, that agreement
        is far stronger evidence than any temperature-diverse consensus.

        Args:
            problem (dict): Problem dict with 'problem_text'.

        Returns:
            tuple[list[Attempt], dict, str | None]: Attempts, vote dict, consensus.
        """
        problem_text = problem["problem_text"]
        attempts: list[Attempt] = []
        answer_counts: Counter = Counter()

        logger.info(f"    [GVR] Approach-diverse generation: {len(APPROACH_KEYS)} frameworks")

        for i, approach_key in enumerate(APPROACH_KEYS):
            self._check_timer()
            approach_name = APPROACH_FRAMEWORKS[approach_key]["name"]
            logger.info(f"    [{i+1}/{len(APPROACH_KEYS)}] Framework: {approach_name}")

            attempt_start = time.time()
            approach_prompt = build_approach_prompt(problem_text, approach_key)

            # Lower temperature — the framework directive drives diversity, not noise
            solution = self._generate_with_tir(
                approach_prompt,
                temperature=0.3,
                max_tokens=self.max_generate_tokens,
            )

            attempt = self._analyze_completed_solution(
                solution=solution,
                attempt_number=i + 1,
                duration_seconds=time.time() - attempt_start,
                approach_framework=approach_key,
                token_ids=getattr(self, '_last_token_ids', None),
                logprobs=getattr(self, '_last_logprobs', None),
            )
            attempts.append(attempt)

            if attempt.extracted_answer is not None:
                weight = self._attempt_vote_weight(attempt)
                answer_counts[attempt.extracted_answer] += weight
                answer = attempt.extracted_answer
                passed = attempt.verification_passed
                logger.info(
                    f"      → {approach_name}: {answer} "
                    f"({'code-verified' if passed else 'unverified'})"
                )
            else:
                logger.info(f"      → {approach_name}: no answer extracted")

        vote_dict = self._score_answers(attempts)
        consensus: str | None = None

        if vote_dict:
            top_answer, top_count = max(vote_dict.items(), key=lambda item: item[1])
            total_votes = sum(vote_dict.values()) or 1.0
            ratio = top_count / total_votes
            logger.info(
                f"    [GVR] Cross-framework vote: '{top_answer}' "
                f"at {ratio:.0%} ({top_count:.2f}/{total_votes:.2f})"
            )
            # 2+ frameworks agreeing = strong cross-validation signal
            leader = self._best_attempt_for_answer(attempts, top_answer)
            if ratio >= 0.40 and self._attempt_is_acceptable(leader):
                consensus = top_answer

        return attempts, vote_dict, consensus

    def _critique_solution(
        self,
        problem_text: str,
        solution: str,
        approach_key: str | None = None,
    ) -> tuple[bool, str]:
        """Adversarial critique of a solution (Aletheia Verifier role).

        Unlike _nl_verify (which rubber-stamps the same model's work), this
        frames the task as an ADVERSARIAL review: assume the solution is wrong
        until proven otherwise. The model must find a specific flaw or explicitly
        confirm correctness.

        Args:
            problem_text (str): The problem being solved.
            solution (str): The solution to critique.
            approach_key (str | None): The framework the solution used, for context.

        Returns:
            tuple[bool, str]: (is_correct, full_critique_text).
                              is_correct=True only on explicit VERDICT: CORRECT.
        """
        approach_context = ""
        if approach_key and approach_key in APPROACH_FRAMEWORKS:
            fw = APPROACH_FRAMEWORKS[approach_key]
            approach_context = (
                f"\n\nContext: This solution used the {fw['name']} approach.\n"
            )

        critique_prompt = (
            f"You are an adversarial reviewer at an IMO problem-checking committee. "
            f"Your role is to FIND ERRORS. Be skeptical. Assume the solution is wrong "
            f"unless every step is airtight.{approach_context}\n\n"
            f"## Problem\n{problem_text}\n\n"
            f"## Solution Under Adversarial Review\n{solution[:4000]}\n\n"
            f"## Your Task\n"
            f"1. Identify the claimed answer (**ANSWER: N** line).\n"
            f"2. Check EVERY algebraic/logical step. Is each step valid?\n"
            f"3. For each Python code block: does the output actually prove the claim?\n"
            f"4. Look for: missing cases, unjustified assumptions, off-by-one errors, "
            f"incorrect formula usage, circular reasoning.\n"
            f"5. Try to construct a counterexample to the claimed answer.\n"
            f"6. After thorough adversarial review:\n"
            f"   - If you find NO errors: respond **VERDICT: CORRECT** + 1-sentence why.\n"
            f"   - If you find an error: respond **VERDICT: ERROR** + describe EXACTLY "
            f"which step is wrong and why (be specific — 'step 3 assumes X but X is "
            f"not proven' is useful; 'this is wrong' is not)."
        )

        response = self._generate_text(
            critique_prompt,
            temperature=0.15,   # Very low — deliberate, careful review
            max_tokens=1536,
        )

        if "VERDICT: CORRECT" in response.upper():
            return True, response
        if "VERDICT: ERROR" in response.upper():
            return False, response
        # Fail-safe: ambiguous output → treat as unverified error
        return False, f"[Critic inconclusive — treated as error]\n{response[:400]}"

    def _revise_with_critique(
        self,
        problem: dict,
        previous_solution: str,
        critique: str,
        approach_key: str | None = None,
        attempt_number: int = 0,
    ) -> Attempt:
        """GVR Reviser: produce a targeted revision based on adversarial critique.

        This is the 'R' in Generator→Verifier→Reviser (Aletheia, 2602.10177).
        The critique provides specific error context, enabling focused correction
        rather than generic retry-from-scratch.

        Args:
            problem (dict): Problem dict.
            previous_solution (str): The solution that had an error.
            critique (str): Specific error description from _critique_solution.
            approach_key (str | None): Original framework (may be abandoned if critique
                                       shows it is fundamentally wrong).
            attempt_number (int): For Attempt.attempt_number field.

        Returns:
            Attempt: The revised attempt.
        """
        problem_text = problem["problem_text"]
        revise_prompt = build_revise_prompt(
            problem_text, previous_solution, critique, approach_key
        )

        attempt_start = time.time()
        solution = self._generate_with_tir(
            revise_prompt,
            temperature=0.4,    # Slightly higher — may need fresh approach
            max_tokens=self.max_generate_tokens,
        )

        return self._analyze_completed_solution(
            solution=solution,
            attempt_number=attempt_number,
            duration_seconds=time.time() - attempt_start,
            approach_framework=f"{approach_key}_revised" if approach_key else "revised",
        )

    def _refine_solution(
        self,
        problem: dict,
        candidate: "Attempt",
        max_iterations: int = 2,
    ) -> "Attempt":
        """Iteratively refine the best candidate by building upon its reasoning chain.

        Unlike revision (which fixes a specific error flagged by critique), this
        method extends a promising or correct solution — filling reasoning gaps,
        adding independent verification paths, and stress-testing the answer.

        Each iteration takes the previous iteration's output as input, producing
        a strictly more rigorous reasoning chain. Early termination if:
          - Answer changes between iterations (instability — stop and return last stable)
          - Timer is exhausted

        Args:
            problem (dict): Problem dict with 'problem_text'.
            candidate (Attempt): The best solution to build upon.
            max_iterations (int): Maximum refinement passes (default 2 to fit time budget).

        Returns:
            Attempt: The most refined attempt (may be the original if refinement failed).
        """
        problem_text = problem["problem_text"]
        current = candidate
        stable_answer = candidate.extracted_answer

        for iteration in range(1, max_iterations + 1):
            self._check_timer()
            logger.info(
                f"    [GVR] Refinement iteration {iteration}/{max_iterations} "
                f"(answer={current.extracted_answer})"
            )

            refine_prompt = build_iterative_refine_prompt(
                problem_text=problem_text,
                previous_solution=current.solution_text,
                previous_answer=current.extracted_answer,
                iteration=iteration,
            )

            attempt_start = time.time()
            solution = self._generate_with_tir(
                refine_prompt,
                temperature=0.25,   # Low — building on existing work, not exploring
                max_tokens=self.max_generate_tokens,
            )

            refined = self._analyze_completed_solution(
                solution=solution,
                attempt_number=current.attempt_number,
                duration_seconds=time.time() - attempt_start,
                approach_framework=f"{current.approach_framework}_refined{iteration}",
            )
            answer = refined.extracted_answer
            passed = refined.verification_passed

            # Stability check: if answer flips, return the last stable result
            if answer is not None and stable_answer is not None and answer != stable_answer:
                logger.info(
                    f"      → Refinement unstable: {stable_answer} → {answer}. "
                    f"Stopping refinement, keeping {stable_answer}."
                )
                return current  # Return last stable, not the flipped version

            if answer is not None:
                stable_answer = answer
            current = refined
            logger.info(
                f"      → Iteration {iteration}: answer={answer} "
                f"({'code-verified' if passed else 'unverified'})"
            )

        return current

    # =========================================================================
    # Lean Controller: Wave Generation + Repair
    # =========================================================================

    def _majority_vote_wave(
        self,
        problem: dict,
        wave_size: int,
        existing_attempts: list[Attempt],
    ) -> list[Attempt]:
        """Generate a single wave of attempts and analyze each.

        Returns only the NEW attempts (does not include existing_attempts).
        """
        problem_text = problem["problem_text"]
        generate_prompt = build_generate_prompt(problem_text)
        attempts: list[Attempt] = []
        base_num = len(existing_attempts)

        if self.enable_tir:
            for i in range(wave_size):
                self._check_timer()
                sol = self._generate_with_tir(
                    generate_prompt,
                    temperature=self.generate_temperature,
                    max_tokens=self.max_generate_tokens,
                )
                attempt = self._analyze_completed_solution(
                    solution=sol,
                    attempt_number=base_num + i + 1,
                    duration_seconds=0,
                    token_ids=getattr(self, '_last_token_ids', None),
                    logprobs=getattr(self, '_last_logprobs', None),
                )
                attempts.append(attempt)
        else:
            solutions = self._generate_batch(
                generate_prompt,
                n=wave_size,
                temperature=self.generate_temperature,
                max_tokens=self.max_generate_tokens,
            )
            batch_tids = getattr(self, '_batch_token_ids', [])
            batch_lprobs = getattr(self, '_batch_logprobs', [])
            for i, sol in enumerate(solutions):
                tids = batch_tids[i] if i < len(batch_tids) else None
                lprobs = batch_lprobs[i] if i < len(batch_lprobs) else None
                attempt = self._analyze_completed_solution(
                    solution=sol,
                    attempt_number=base_num + i + 1,
                    duration_seconds=0,
                    token_ids=tids,
                    logprobs=lprobs,
                )
                attempts.append(attempt)

        return attempts

    def _single_repair_attempt(
        self,
        problem: dict,
        attempts: list[Attempt],
        problem_text: str,
    ) -> Attempt | None:
        """Run exactly one self-correction attempt to clean up a dirty trace."""
        best = self._best_attempt(attempts)
        if best is None:
            return None

        self._check_timer()
        error_message = self._build_attempt_feedback(best)
        correct_prompt = build_correct_prompt(
            problem_text, best.solution_text, error_message,
        )

        solution = self._generate_with_tir(
            correct_prompt,
            temperature=self.correct_temperature,
            max_tokens=self.max_correct_tokens,
        )

        return self._analyze_completed_solution(
            solution=solution,
            attempt_number=len(attempts) + 1,
            duration_seconds=0,
        )

    def _research_problem_lean(
        self,
        problem: dict,
        trace: ResearchTrace,
        problem_start: float,
        problem_text: str,
    ) -> ResearchTrace:
        """Lean submission controller: wave-based generation with answer-group
        early stopping. Separates hygiene flaws from hard contradictions.

        Flow:
          Wave 1 (4 attempts) → submit-safe? (≥3 support, ≥60% share)
          Wave 2 (4 more)     → submit-safe? (≥4 support, ≥50% share)
          Bounded repair (1)  → submit-safe? (≥3 support, ≥45% share)
          Wave 3 (if budget)  → final AnswerSelector pick
        """
        self._check_timer()

        def _finalize(strategy: str) -> ResearchTrace:
            trace.total_duration_seconds = time.time() - problem_start
            trace.total_attempts = len(trace.attempts)
            trace.majority_vote_answers = self._score_answers(trace.attempts)
            logger.info(
                f"  [{strategy.upper()}] answer={trace.final_answer} "
                f"({trace.total_attempts} attempts, "
                f"{trace.total_duration_seconds:.1f}s)"
            )
            return trace

        # --- Wave 1: 4 attempts ---
        logger.info("    [Lean] Wave 1: generating 4 attempts...")
        wave1 = self._majority_vote_wave(problem, wave_size=4, existing_attempts=[])
        trace.attempts.extend(wave1)

        groups = self._build_answer_groups(trace.attempts)
        safe, reason = self._is_submit_safe(
            groups, len(trace.attempts), min_support=3, min_share=0.60,
        )
        if safe:
            trace.final_answer = str(groups[0].answer)
            trace.solved = True
            trace.strategy = "lean_wave1"
            return _finalize("lean_wave1")

        # --- Wave 2: 4 more (total 8) ---
        self._check_timer()
        logger.info("    [Lean] Wave 2: generating 4 more attempts...")
        wave2 = self._majority_vote_wave(
            problem, wave_size=4, existing_attempts=trace.attempts,
        )
        trace.attempts.extend(wave2)

        groups = self._build_answer_groups(trace.attempts)
        safe, reason = self._is_submit_safe(
            groups, len(trace.attempts), min_support=4, min_share=0.50,
        )
        if safe:
            trace.final_answer = str(groups[0].answer)
            trace.solved = True
            trace.strategy = "lean_wave2"
            return _finalize("lean_wave2")

        # --- Bounded repair: if leader is stable but traces are dirty ---
        if groups and len(groups[0].attempts) >= 2 and not groups[0].has_clean_trace:
            logger.info(
                f"    [Lean] Repair: leader answer={groups[0].answer} "
                f"with {len(groups[0].attempts)} dirty traces, attempting repair..."
            )
            repair = self._single_repair_attempt(
                problem, trace.attempts, problem_text,
            )
            if repair is not None:
                trace.attempts.append(repair)
                groups = self._build_answer_groups(trace.attempts)
                safe, reason = self._is_submit_safe(
                    groups, len(trace.attempts), min_support=3, min_share=0.45,
                )
                if safe:
                    trace.final_answer = str(groups[0].answer)
                    trace.solved = True
                    trace.strategy = "lean_repaired"
                    return _finalize("lean_repaired")

        # --- Wave 3 (if budget remains) ---
        problem_time_left = (
            getattr(self, '_problem_deadline', float('inf')) - time.time()
        )
        if self._remaining_seconds() > 120 and problem_time_left > 60:
            self._check_timer()
            logger.info("    [Lean] Wave 3: generating 4 more attempts...")
            wave3 = self._majority_vote_wave(
                problem, wave_size=4, existing_attempts=trace.attempts,
            )
            trace.attempts.extend(wave3)

        # --- Final selection via AnswerSelector ---
        ans, sel_reason, sel_conf, _ = self._select_answer_from_attempts(
            trace.attempts,
        )
        if ans is not None:
            trace.final_answer = ans
            trace.solved = True
            trace.strategy = "lean_final_select"
            return _finalize("lean_final_select")

        trace.strategy = "lean_exhausted"
        return _finalize("lean_exhausted")

    def _research_problem_gvr(
        self,
        problem: dict,
        trace: ResearchTrace,
        problem_start: float,
        problem_text: str,
    ) -> ResearchTrace:
        """Approach-Diverse Generator → Verifier → Reviser loop.

        Replaces temperature-diverse majority vote with semantically diverse
        generation across 4 mathematical frameworks, followed by adversarial
        critique and targeted revision for low-confidence candidates.

        Flow:
          Phase 1: Generate 4 approach-diverse solutions
          Phase 2: If cross-framework consensus → done (fast path)
          Phase 3: Adversarial critique of top-2 candidates by vote
                   → if correct: confidence boost
                   → if error found: targeted revision
          Phase 4: Re-evaluate post-revision votes
          Phase 5: GenSelect on all candidates if still no consensus
          Phase 6: Exhausted fallback

        Args:
            problem (dict): Problem dict.
            trace (ResearchTrace): Initialized trace to populate.
            problem_start (float): Wall-clock timestamp of problem start.
            problem_text (str): Problem text.

        Returns:
            ResearchTrace: Fully populated trace.
        """
        self._check_timer()

        # --- Phase 1: Approach-diverse generation ---
        logger.info("    [GVR] Phase 1: Approach-diverse generation")
        attempts, vote_dict, consensus = self._generate_approach_diverse(problem)

        for i, att in enumerate(attempts):
            att.attempt_number = i + 1
        trace.attempts.extend(attempts)
        trace.majority_vote_answers = vote_dict

        if consensus is not None and self._attempt_is_acceptable(
            self._best_attempt_for_answer(trace.attempts, consensus)
        ):
            trace.final_answer = consensus
            trace.solved = True
            trace.strategy = "gvr_approach_diverse"
            trace.total_duration_seconds = time.time() - problem_start
            trace.total_attempts = len(trace.attempts)
            logger.info(f"  SOLVED (GVR cross-framework): {consensus}")
            return trace

        # --- Phase 2: Adversarial critique + targeted revision ---
        # Only critique the top-2 vote-getters to save time budget
        logger.info("    [GVR] Phase 2: Adversarial critique + revision")
        revised_counts: Counter = Counter(vote_dict)
        revised_attempts: list[Attempt] = []

        # Order by vote weight descending; critique up to 2
        candidates = sorted(
            [a for a in attempts if a.extracted_answer is not None],
            key=lambda a: vote_dict.get(a.extracted_answer or "", 0),
            reverse=True,
        )[:2]

        for att in candidates:
            self._check_timer()
            approach_key = att.approach_framework or None
            approach_name = APPROACH_FRAMEWORKS.get(approach_key or "", {}).get("name", approach_key)
            logger.info(
                f"    [GVR] Critiquing {approach_name} (answer={att.extracted_answer})..."
            )

            is_correct, critique_text = self._critique_solution(
                problem_text, att.solution_text, approach_key
            )

            if is_correct:
                logger.info(f"      → Critique: CORRECT — boosting confidence")
                # Boost: critique-verified is equivalent to one extra code-verified vote
                if att.extracted_answer:
                    revised_counts[att.extracted_answer] += max(
                        1.0,
                        self._attempt_vote_weight(att) * 0.5,
                    )
            else:
                logger.info(f"      → Critique: ERROR — revising...")
                revised_att = self._revise_with_critique(
                    problem,
                    att.solution_text,
                    critique_text,
                    approach_key,
                    attempt_number=len(trace.attempts) + len(revised_attempts) + 1,
                )
                revised_attempts.append(revised_att)

                if revised_att.extracted_answer is not None:
                    # Revision with code verification is high-value signal
                    weight = self._attempt_vote_weight(revised_att)
                    revised_counts[revised_att.extracted_answer] += weight
                    logger.info(
                        f"      → Revised: {revised_att.extracted_answer} "
                        f"({'verified' if revised_att.verification_passed else 'unverified'})"
                    )
                else:
                    logger.info(f"      → Revision: no answer extracted")

        trace.attempts.extend(revised_attempts)

        # --- Phase 3: Re-evaluate post-revision consensus ---
        if revised_counts:
            top_answer, top_count = revised_counts.most_common(1)[0]
            total_votes = sum(revised_counts.values())
            ratio = top_count / total_votes
            logger.info(
                f"    [GVR] Post-revision vote: '{top_answer}' "
                f"at {ratio:.0%} ({top_count}/{total_votes})"
            )
            # More lenient threshold: critique + revision evidence is higher quality
            leader = self._best_attempt_for_answer(trace.attempts, top_answer)
            if ratio >= 0.35 and self._attempt_is_acceptable(leader):
                consensus = top_answer

        if consensus is not None and self._attempt_is_acceptable(
            self._best_attempt_for_answer(trace.attempts, consensus)
        ):
            trace.final_answer = consensus
            trace.solved = True
            trace.strategy = "gvr_critique_revised"
            trace.total_duration_seconds = time.time() - problem_start
            trace.total_attempts = len(trace.attempts)
            logger.info(f"  SOLVED (GVR+critique): {consensus}")
            return trace

        # --- Phase 4: Iterative refinement of the leading candidate ---
        # If no consensus yet, pick the current vote leader and iteratively refine it.
        # Refinement builds upon the existing reasoning chain (fills gaps, adds
        # independent verification, stress-tests the answer) rather than starting fresh.
        all_with_answers_pre = [a for a in trace.attempts if a.extracted_answer is not None]
        if all_with_answers_pre:
            self._check_timer()
            # Leader by revised_counts (incorporates critique boost + revision votes)
            leader = max(
                all_with_answers_pre,
                key=lambda a: revised_counts.get(a.extracted_answer or "", 0),
            )
            logger.info(
                f"    [GVR] Phase 4: Iterative refinement of leader (answer={leader.extracted_answer})"
            )
            refined = self._refine_solution(problem, leader, max_iterations=2)
            refined.attempt_number = len(trace.attempts) + 1
            trace.attempts.append(refined)

            if refined.extracted_answer is not None:
                weight = self._attempt_vote_weight(refined)
                revised_counts[refined.extracted_answer] += weight
                logger.info(
                    f"      → Refined answer: {refined.extracted_answer} "
                    f"({'verified' if refined.verification_passed else 'unverified'})"
                )

            # Re-check consensus after refinement
            if revised_counts:
                top_answer, top_count = revised_counts.most_common(1)[0]
                total_votes = sum(revised_counts.values())
                ratio = top_count / total_votes
                logger.info(
                    f"    [GVR] Post-refinement vote: '{top_answer}' "
                    f"at {ratio:.0%} ({top_count}/{total_votes})"
                )
                leader = self._best_attempt_for_answer(trace.attempts, top_answer)
                if ratio >= 0.35 and self._attempt_is_acceptable(leader):
                    consensus = top_answer

            if consensus is not None and self._attempt_is_acceptable(
                self._best_attempt_for_answer(trace.attempts, consensus)
            ):
                trace.final_answer = consensus
                trace.solved = True
                trace.strategy = "gvr_refined"
                trace.total_duration_seconds = time.time() - problem_start
                trace.total_attempts = len(trace.attempts)
                logger.info(f"  SOLVED (GVR+refinement): {consensus}")
                return trace

        # --- Phase 5: GenSelect on all candidates ---
        all_with_answers = [a for a in trace.attempts if a.extracted_answer is not None]
        if len(all_with_answers) >= 2:
            self._check_timer()
            logger.info("    [GVR] Phase 5: GenSelect on all candidates...")
            genselect_answer = self._genselect(problem, all_with_answers)
            if genselect_answer is not None and self._attempt_is_acceptable(
                self._best_attempt_for_answer(trace.attempts, genselect_answer)
            ):
                trace.final_answer = genselect_answer
                trace.solved = True
                trace.strategy = "gvr_genselect"
                trace.total_duration_seconds = time.time() - problem_start
                trace.total_attempts = len(trace.attempts)
                logger.info(f"  SOLVED (GVR+GenSelect): {genselect_answer}")
                return trace

        # --- Phase 6: Exhausted — pick best available ---
        trace.strategy = "gvr_exhausted"
        best_remaining = self._best_attempt(trace.attempts)
        if best_remaining is not None and best_remaining.extracted_answer is not None:
            trace.final_answer = best_remaining.extracted_answer

        trace.total_duration_seconds = time.time() - problem_start
        trace.total_attempts = len(trace.attempts)
        logger.warning(
            f"  [GVR EXHAUSTED] {trace.total_attempts} attempts, "
            f"best answer: {trace.final_answer}"
        )
        return trace

    # =========================================================================
    # Research Loop (v2)
    # =========================================================================

    def research_problem(self, problem: dict) -> ResearchTrace:
        """Full research loop for one problem.

        Process:
        1. Majority vote (N parallel samples)
        2. If consensus found → optional NL verify → done
        3. If no consensus → self-correct top candidate

        Args:
            problem (dict): Dict with keys: id, problem_text, source, difficulty.

        Returns:
            ResearchTrace: The trace containing all attempts and the final result.
        """
        problem_start = time.time()
        problem_id = problem.get("id", "unknown")
        problem_text = problem["problem_text"]
        source = problem.get("source", "unknown")
        difficulty = problem.get("difficulty", "unknown")

        trace = ResearchTrace(
            problem_id=problem_id,
            problem_text=problem_text,
            source=source,
            difficulty=difficulty,
        )

        logger.info(
            f"[{self._elapsed_str()}] Researching problem {problem_id} "
            f"({source}, {difficulty}) | Remaining: {self._remaining_str()}"
        )

        # --- Topic Classification: inject domain-specific strategy hints ---
        original_system_prompt = self.system_prompt
        topic = classify_topic(problem_text)
        augmented_problem_text = problem_text
        if topic and topic in TOPIC_PATCHES:
            self.system_prompt = build_system_prompt(TOPIC_PATCHES[topic])
            logger.info(f"    Topic classified: {topic} (injecting strategy patch)")
        else:
            logger.info(f"    Topic: unclassified (using baseline prompt)")

        if topic == "geometry":
            augmented_problem_text = self._maybe_run_geometry_backend(
                problem=problem,
                problem_text=problem_text,
                topic=topic,
            )

        working_problem = dict(problem)
        working_problem["problem_text"] = augmented_problem_text

        try:
            return self._research_problem_inner(
                working_problem,
                trace,
                problem_start,
                augmented_problem_text,
            )
        finally:
            # Always restore original system prompt to avoid topic leak
            self.system_prompt = original_system_prompt

    def _research_problem_inner(
        self,
        problem: dict,
        trace: ResearchTrace,
        problem_start: float,
        problem_text: str,
    ) -> ResearchTrace:
        """Inner research loop: dispatches to GVR then falls back to self-correction.

        Primary path: approach-diverse GVR (4 frameworks → critique → revision).
        Fallback: if GVR exhausts without answer, run self-correction on best attempt.

        Args:
            problem (dict): The problem dict.
            trace (ResearchTrace): The initialized trace to populate.
            problem_start (float): The timestamp when processing began.
            problem_text (str): The raw text of the problem.

        Returns:
            ResearchTrace: The fully populated trace.
        """
        # --- Lean submission controller (wave-based, answer-group early stop) ---
        if self.submission_mode:
            return self._research_problem_lean(
                problem, trace, problem_start, problem_text,
            )

        # --- Primary path: Approach-Diverse GVR ---
        trace = self._research_problem_gvr(problem, trace, problem_start, problem_text)

        # Fast-exit: GVR solved it
        if trace.solved:
            return trace

        # --- Fallback: Self-Correction on best GVR attempt ---
        logger.info("    [Fallback] GVR exhausted — trying self-correction...")
        attempts = trace.attempts
        consensus, sel_reason, sel_conf, vote_dict = self._select_answer_from_attempts(attempts)

        # --- Phase 4A: AnswerSelector (confidence-weighted, typed) ---
        if _HAS_ANSWER_SELECTOR and _answer_selector is not None:
            _sel_answer, sel_reason, sel_conf = _answer_selector.select([
                AnnotatedSolution(
                    final_answer=int(a.extracted_answer) if a.extracted_answer is not None else None,
                    report=VerificationReport(
                        passed_checks=1 if a.verification_passed else 0,
                        # Code-verified answers get ENUMERATED weight (4.0×) vs
                        # unverified NL_JUDGMENT (1.0×).  This is the key signal:
                        # if the model's code ran and produced the right format,
                        # that attempt is more trustworthy than prose-only ones.
                        confidence=(
                            ConfidenceLevel.ENUMERATED
                            if a.verification_passed and a.extracted_answer is not None
                            else ConfidenceLevel.NL_JUDGMENT
                            if a.extracted_answer is not None
                            else ConfidenceLevel.UNVERIFIED
                        ),
                    ),
                    attempt_id=a.attempt_number,
                    raw_text=a.solution_text,
                )
                for a in attempts
            ])
            if _sel_answer is not None:
                consensus = str(_sel_answer)
                logger.info(
                    f"    AnswerSelector: {_sel_answer} "
                    f"(reason={sel_reason}, conf={sel_conf:.2f})"
                )

        if consensus is not None:
            logger.info(
                f"    AnswerSelector: {consensus} "
                f"(reason={sel_reason}, conf={sel_conf:.2f})"
            )
            if not self._attempt_is_acceptable(
                self._best_attempt_for_answer(attempts, consensus)
            ):
                logger.info(
                    "    Typed verifier/flaw detector rejected the leading answer; "
                    "escalating to self-correction."
                )
                consensus = None

        # --- Phase 1B: GenSelect (if weak consensus) ---
        if consensus is not None:
            # Check if consensus is weak (< 40% of weighted votes)
            total_votes = sum(vote_dict.values()) if vote_dict else 0
            top_votes = vote_dict.get(consensus, 0) if vote_dict else 0
            consensus_strength = top_votes / total_votes if total_votes > 0 else 0

            if consensus_strength < 0.4 and len(attempts) >= 4:
                # Weak consensus — try GenSelect for a better pick
                logger.info(
                    f"    Weak consensus ({consensus_strength:.0%}), "
                    f"trying GenSelect..."
                )
                genselect_answer = self._genselect(problem, attempts)
                if genselect_answer is not None and self._attempt_is_acceptable(
                    self._best_attempt_for_answer(attempts, genselect_answer)
                ):
                    consensus = genselect_answer
                    logger.info(f"    GenSelect overrode majority vote → '{consensus}'")

        if consensus is not None:
            # Optional NL verification of the consensus answer
            best_candidate = self._best_attempt_for_answer(attempts, consensus)
            best_solution = best_candidate.solution_text if best_candidate is not None else None

            if best_solution and self.enable_nl_verify:
                nl_ok, nl_msg = self._nl_verify(problem_text, best_solution)
                logger.info(f"    NL Verify: {nl_msg[:80]}")
                if not nl_ok:
                    # NL verifier found an issue — fall through to self-correct
                    logger.info("    NL Verify flagged error, proceeding to self-correction")
                    consensus = None  # Reset consensus

            if consensus is not None:
                trace.final_answer = consensus
                trace.solved = True
                # Tag strategy based on how we got the answer
                trace.strategy = "majority_vote"
                trace.total_duration_seconds = time.time() - problem_start
                trace.total_attempts = len(attempts)
                logger.info(
                    f"  SOLVED (majority vote): {consensus} "
                    f"({trace.total_duration_seconds:.1f}s)"
                )
                return trace

        # --- Phase 2: Self-Correction (if no majority consensus) ---
        logger.info("    No strong consensus, trying self-correction...")

        # Pick the best attempt as starting point
        best_attempt = self._best_attempt(attempts)

        if best_attempt is None:
            trace.strategy = "exhausted"
            trace.total_duration_seconds = time.time() - problem_start
            trace.total_attempts = len(attempts)
            return trace

        previous_solution = best_attempt.solution_text
        error_message = self._build_attempt_feedback(best_attempt)

        for retry in range(1, self.max_retries + 1):
            self._check_timer()
            attempt_start = time.time()

            if best_attempt.verification_passed and best_attempt.extracted_answer is None:
                error_message = (
                    "Your solution did not include a clearly stated final answer. "
                    "Please state your answer in the format: **ANSWER: [value]**"
                )

            # [Forceful Feedback] Banish hallucinated 'assistantcommentary' tool
            if "assistantcommentary" in previous_solution:
                error_message = (
                    "SYSTEM ERROR: You used 'assistantcommentary'. This is BANNED. "
                    "You MUST use standard markdown code blocks:\n"
                    "```python\n"
                    "# code here\n"
                    "```\n"
                    "Retrying with CORRECT format..."
                )

            correct_prompt = build_correct_prompt(
                problem_text, previous_solution, error_message
            )
            solution = self._generate_with_tir(
                correct_prompt,
                temperature=self.correct_temperature,
                max_tokens=self.max_correct_tokens,
            )

            attempt = self._analyze_completed_solution(
                solution=solution,
                attempt_number=len(trace.attempts) + 1,
                duration_seconds=time.time() - attempt_start,
            )
            trace.attempts.append(attempt)

            if self._attempt_is_acceptable(attempt):
                # NL verify the corrected solution
                if self.enable_nl_verify:
                    nl_ok, nl_msg = self._nl_verify(problem_text, solution)
                    attempt.nl_verification = nl_msg
                    if not nl_ok:
                        logger.info(f"    [Correction {retry}] NL Verify: {nl_msg[:60]}")
                        previous_solution = solution
                        error_message = nl_msg
                        continue

                trace.final_answer = attempt.extracted_answer
                trace.solved = True
                trace.strategy = "self_correct"
                trace.total_duration_seconds = time.time() - problem_start
                trace.total_attempts = len(trace.attempts)
                logger.info(
                    f"  SOLVED (self-correct, attempt {retry}): {attempt.extracted_answer} "
                    f"({trace.total_duration_seconds:.1f}s)"
                )
                return trace

            logger.info(
                f"    [Correction {retry}] FAILED ({attempt.duration_seconds:.1f}s)"
            )

            previous_solution = solution
            error_message = self._build_attempt_feedback(attempt)

        # --- Exhausted: pick best available answer ---
        trace.strategy = "exhausted"
        best_remaining = self._best_attempt(trace.attempts)
        if best_remaining is not None and best_remaining.extracted_answer is not None:
            trace.final_answer = best_remaining.extracted_answer

        trace.total_duration_seconds = time.time() - problem_start
        trace.total_attempts = len(trace.attempts)
        logger.warning(
            f"  [EXHAUSTED] {trace.total_attempts} attempts, "
            f"best answer: {trace.final_answer}"
        )
        return trace

    # =========================================================================
    # Dynamic Time Allocation
    # =========================================================================

    def _compute_time_budget(
        self, problems_remaining: int, difficulty: str
    ) -> float:
        """Compute per-problem time budget based on remaining time and difficulty.

        Args:
            problems_remaining (int): Number of problems left in the queue.
            difficulty (str): Categorical difficulty string ("easy", "medium", "hard", "extreme").

        Returns:
            float: Maximum seconds to spend on this problem.
        """
        remaining = self._remaining_seconds()
        if problems_remaining <= 0:
            return remaining

        base_budget = remaining / problems_remaining

        # Difficulty multipliers
        multipliers = {
            "easy": 0.6,
            "medium": 1.0,
            "hard": 1.5,
            "extreme": 2.0,
        }
        mult = multipliers.get(difficulty, 1.0)

        # Cap at 80% of remaining time (leave buffer for other problems)
        budget = min(base_budget * mult, remaining * 0.8)

        return max(budget, 60)  # Minimum 60 seconds per problem

    # =========================================================================
    # Main Execution
    # =========================================================================

    def run(self, problems: list[dict], output_path: str) -> dict:
        """Main execution loop. Processes problems with a hard timer.

        Args:
            problems (list[dict]): List of problem dictionaries to process.
            output_path (str): File path to write the resulting JSONL data.

        Returns:
            dict: Summary statistics covering solve rates and completion times.
        """
        self.start_time = time.time()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        total = len(problems)
        solved = 0
        attempted = 0
        traces = []

        logger.info("=" * 60)
        logger.info("DEEP RESEARCHER v2 — H100 Research Sprint")
        logger.info("=" * 60)
        logger.info(f"  Model:       {self.model_path}")
        logger.info(f"  Family:      {self.model_family}")
        logger.info(f"  Problems:    {total}")
        logger.info(f"  Time limit:  {self.time_limit_hours:.1f} hours")
        logger.info(f"  Samples/Q:   {self.num_samples}")
        logger.info(f"  Max retries: {self.max_retries}")
        logger.info(f"  TIR:         {'ON' if self.enable_tir else 'OFF'}")
        logger.info(f"  NL Verify:   {'ON' if self.enable_nl_verify else 'OFF'}")
        logger.info(f"  Max tokens:  {self.max_generate_tokens}")
        logger.info(f"  Output:      {output_path}")
        logger.info(f"  Dry run:     {self.dry_run}")
        logger.info("=" * 60)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for i, problem in enumerate(problems):
                    self._check_timer()

                    problems_remaining = total - i
                    difficulty = problem.get("difficulty", "medium")
                    budget = self._compute_time_budget(problems_remaining, difficulty)
                    self._problem_deadline = time.time() + budget

                    logger.info(
                        f"\n--- Problem {i + 1}/{total} "
                        f"(budget: {budget / 60:.1f}min) ---"
                    )

                    # Reset per-problem confidence threshold for DeepConf
                    if hasattr(self, '_confidence_threshold'):
                        del self._confidence_threshold

                    trace = self.research_problem(problem)
                    traces.append(trace)
                    attempted += 1

                    if trace.solved:
                        solved += 1

                    # Crash-safe write: flush after every problem
                    f.write(json.dumps(trace.to_dict(), ensure_ascii=False) + "\n")
                    f.flush()

                    # Progress report
                    rate = solved / attempted if attempted > 0 else 0
                    logger.info(
                        f"  Progress: {attempted}/{total} attempted, "
                        f"{solved} solved ({rate:.0%}) | "
                        f"Elapsed: {self._elapsed_str()} | "
                        f"Remaining: {self._remaining_str()}"
                    )

        except TimeLimitExceeded as e:
            logger.warning(f"\n{'=' * 60}")
            logger.warning(f"GRACEFUL EXIT: {e}")
            logger.warning(f"{'=' * 60}")

        except Exception as e:
            logger.error(f"\nUNEXPECTED ERROR: {type(e).__name__}: {e}")
            raise

        # Final summary
        elapsed = time.time() - self.start_time
        strategy_counts = Counter(t.strategy for t in traces)

        summary = {
            "total_problems": total,
            "attempted": attempted,
            "solved": solved,
            "solve_rate": solved / attempted if attempted > 0 else 0,
            "elapsed_seconds": elapsed,
            "elapsed_hours": elapsed / 3600,
            "output_file": output_path,
            "avg_time_per_problem": elapsed / attempted if attempted > 0 else 0,
            "strategies": dict(strategy_counts),
            "model": self.model_path,
            "model_family": self.model_family,
            "num_samples": self.num_samples,
            "tir_enabled": self.enable_tir,
            "nl_verify_enabled": self.enable_nl_verify,
        }

        logger.info(f"\n{'=' * 60}")
        logger.info("RESEARCH SPRINT COMPLETE")
        logger.info(f"{'=' * 60}")
        logger.info(f"  Attempted:  {attempted}/{total}")
        logger.info(f"  Solved:     {solved}/{attempted} ({summary['solve_rate']:.0%})")
        logger.info(f"  Strategies: {dict(strategy_counts)}")
        logger.info(f"  Elapsed:    {self._elapsed_str()}")
        logger.info(f"  Avg/prob:   {summary['avg_time_per_problem']:.1f}s")
        logger.info(f"  Output:     {output_path}")
        logger.info(f"{'=' * 60}")

        # Write summary to separate file
        summary_path = str(output_file.with_suffix(".summary.json"))
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"  Summary:    {summary_path}")

        return summary
