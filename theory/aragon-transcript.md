\[00:00:01\] hey everybody so more and more people in general have been asking me for uh more like uh like verifiable

\[00:00:08\] proof benchmarks etc around my framework which is of like that's expected of course right uh and then uh within

\[00:00:14\] that like I've released like a lot of research benchmarks etc that people could go off of but I have

\[00:00:20\] like I haven't done it um very explicitly um within this and then so that's what I want to demonstrate

\[00:00:27\] very specifically today is benchmark testing geometric structure versus pure scale directly uh and then showcasing the results and uh

\[00:00:37\] how the experiment went within that uh and then so overall like I'm going to go off of a script

\[00:00:43\] within this like so I I've gone both ways with the script and without and then like people have commented

\[00:00:47\] both ways like uh like like when I don't use a script it's like oh you should use a script

\[00:00:51\] and then when I do it's like oh you're just reading like an AI script or whatever um so my

\[00:00:55\] preference is a script if people are going to just comment both ways uh so I'll I'll just go with

\[00:01:00\] the script so for the last several years the dominant story in AI has been simple if you want better

\[00:01:07\] performance make the model bigger more parameters more data more compute and to be fair that story has worked scale

\[00:01:15\] has produced systems with astonishing breadth but scale has also trained us into a dangerous habit treating intelligence as if

\[00:01:23\] it were mostly a volume problem as if the path to better behavior is just more capacity poured into the

\[00:01:30\] same basic container our experiments suggest something else not that scale is useless not that larger models never help but

\[00:01:40\] that there are regimes especially multitask regimes with internal conflict where structure matters more than size in those settings the

\[00:01:50\] decisive question is not how big is the model but how is the model organized that is the difference between

\[00:01:58\] a pure scale and geometric structure the core idea a model does not just store information it arranges it the

\[00:02:08\] arrangement matters if two tasks share the same representation too aggressively they interfere with each other the model h may

\[00:02:18\] have enough parameters in principle yet still perform worse because its internal geometry is poorly organized knowledge and behavior begin

\[00:02:27\] to collide inside the same latent channels capacity exists but capability is muddled this is the hidden weakness of pure

\[00:02:36\] scale a larger model can sometimes brute force its way around that weakness but brute force is not the same

\[00:02:44\] thing as a clean solution if the internal organization remains entangled then adding parameters may simply give the model more

\[00:02:53\] room to compensate for confusion rather than eliminate it geometric structure attacks the problem at a deeper level instead of

\[00:03:02\] only asking for more capacity it asks for better separation better routing and cleaner task organization inside the latent space

\[00:03:11\] itself that's the difference between a bigger warehouse and a better city plan so what exactly we tested to examine

\[00:03:21\] this directly we built a controlled multitask experiment each model received the same type of synthetic sequence input and had

\[00:03:29\] to perform two different tasks on the same input task one was a sentiment-like binary classification task and task two

\[00:03:37\] was a counting/structured extraction task these tasks were intentionally chosen because they draw on different abstractions while sharing the same

\[00:03:45\] underlying sequence that makes them useful for studying interference one task is more semantic the other is more exact and

\[00:03:54\] structured both compete for representational resources we compared four model types one was a baseline small a small shared encoder

\[00:04:04\] with both tasks using the same pulled representation two was a bigger baseline the same architecture but four times bigger

\[00:04:12\] three was adapter only small the small the same small encoder but with task specific adapters branching off the shared

\[00:04:20\] representation and then four was a geometry small the adapter version plus an orthogonality pressure encouraging the task specific representations

\[00:04:29\] to remain geometrically separated and then so within this and highlighting this method within that like this particular method this

\[00:04:37\] framework overall is a very simplistic um implementation of the geometry framework this setup lets us isolate three different hypotheses

\[00:04:48\] does a simple scaling help does branching or task specific routing help and does explicit geometric separation help beyond routing

\[00:04:56\] alone why this matters most people assume that a larger model should dominate a smaller one and if the smaller

\[00:05:02\] one wins many assume it must be some narrow flu but that assumption only holds if the main bottleneck is

\[00:05:10\] raw capacity in a multitask the bottleneck is often not capacity it's interference a model may know enough to solve

\[00:05:21\] both tasks but fail because the same latent machinery is being pulled in incompatible directions in that case scale is

\[00:05:31\] not solving the real problem it's just absorbing the damage and then I'll showcase to you actually making this particular

\[00:05:38\] problem worse via just pure scale geometric structure by contrast tries to reduce the damage directly that is why this

\[00:05:48\] experiment matters it's not just about getting a slightly better score it's about asking whether a model can be made

\[00:05:54\] better by organizing its internal space more intelligently rather than merely enlarging it before I move on from this just

\[00:06:02\] like the simplest overall framing that I can put for this and it like uh it's very straightforward to me

\[00:06:08\] right so the current and standard approach to AI is just blindly uh uh like guiding the model and optimizing

\[00:06:16\] the model via stoastic gradient descent no matter what all the time that's all you do is you're just blindly

\[00:06:21\] guiding based off of that no other measurements whatsoever and then the uh second thing is is that you're like

\[00:06:27\] dumping all of this content into one singular latent space right like a and and and this just just this

\[00:06:33\] giant big blob and there's literally no internal structure within this blob until the model creates that structure itself and

\[00:06:43\] then so just knowing that just giving it some geometric helpers uh is all that we're doing and testing within

\[00:06:51\] that and then so what the first results showed in the initial regime the geometry aware model performed extremely well

\[00:06:57\] it achieved the best average accuracy best test loss strongest sentiment performance and almost perfect count behavior more importantly it

\[00:07:05\] did this with a model that was still small the larger baseline despite having roughly four times the parameter count

\[00:07:12\] did not dominate it the most striking result was in representation overlap the shared baselines remained completely entangled under the

\[00:07:21\] overlap measure their task representations were effectively the same space the geometry aware model by contrast rapidly drove overlap down

\[00:07:32\] toward zero this meant that the structure was not decorative it was actually changing how the model organized its internal

\[00:07:40\] representations that matters because a lot of regularization tricks look impressive in theory but do very little in practice this

\[00:07:49\] one clearly altered the latent behavior the first experiment suggested a strong conclusion better internal organization can outperform naive scaling

\[00:08:01\] when the real problem is interference rather than under capacity the key ablation branching versus orthogonality that first result was

\[00:08:12\] promising but it was not yet enough a skeptic could reasonably say maybe the win had nothing to do with

\[00:08:18\] geometry maybe all of the benefit came from adding task specific branches in other words perhaps the important ingredient was

\[00:08:27\] routing and not separation so we ran the correct ablation we added adapter only small which had the same task

\[00:08:35\] specific branching but no orthogonality pressure this clarified the story considerably branching helped that part became obvious compared to the

\[00:08:46\] fully shared small baseline the adapter only model improved test loss improved such accuracy slightly and dramatically reduced representation overlap

\[00:08:57\] that meant task specific routing alone already changed the game the model benefited simply from not forcing both tasks through

\[00:09:05\] the same exact final representation channel but branching alone was not the whole story when we compared geometry small to

\[00:09:14\] adapter only small the orthogonality term still added value it further reduced overlap improved test loss and improved structured task

\[00:09:24\] performance and sharpened calibration in other words routing gave the model separate lanes geometric pressure made those lanes cleaner that

\[00:09:34\] is a very important distinction it means that the improvement was not just give each task its own adapter which

\[00:09:41\] is like what everyone is calling all of the breakthroughs all of a sudden right the model improved further when

\[00:09:48\] we encourage those task representations to remain genuinely distinct so the emerging picture became shared representation is weak under interference

\[00:09:59\] branching provides a major structural gain and geometric separation provides an additional refinement gain that's already a meaningful result the

\[00:10:10\] harder regime where scaling like absolutely broke the decisive test came when we increased task conflict we made the data

\[00:10:18\] set substantially harsher stronger anti-correlation between count and sentiment more negative distractors when the count signal is high and weaker

\[00:10:26\] clean positive signal and more noise essentially the common things that are being tried to solve for via scale right

\[00:10:34\] if we uh if a model encounters these problems the common logic is is that scale could overcome them this

\[00:10:41\] is where architecture gets tested for real easy task can hide structural weaknesses hard conflict exposes them and in the

\[00:10:48\] hard conflict regime the larger baseline got exposed badly it had the worst loss the worst average accuracy and the

\[00:10:58\] worst sentiment accuracy and it still remained fully entangled in representation space that is not subtle that is exactly the

\[00:11:07\] kind of result that challenges the pure scale narrative the adapter only model held up much better it preserved strong

\[00:11:14\] performance and clearly improved task separation so routing mattered even more once conflict increased but the geometryaware model delivered the

\[00:11:25\] cleanest overall solution it achieved the best test loss by a meaningful margin the best calibration nearperfect structure performance and

\[00:11:34\] by far the strongest representational separation there was a small trade-off the adapter only model slightly edged it on raw

\[00:11:43\] average accuracy but the geometry model had the cleaner optimization profile cleaner calibration and vastly stronger latent factorization that is

\[00:11:52\] what a real structural bias often looks like it doesn't always maximize the flashiest topline number instead it produces a

\[00:12:01\] more stable and internally coherent solution in the hard regime the conclusion became much stronger when task conflict becomes substantial

\[00:12:11\] scale alone does not solve the problem structural organization does provably what geometric structure really means here it's easy to

\[00:12:22\] hear a phrase like geometric structure and imagine handwavy mysticism that is not what's happening in this context geometric structure

\[00:12:30\] means something concrete task specific routing instead of total sharing representational separation instead of force overlap and latent organization that

\[00:12:40\] reflects the task the fact that different tasks require different subspaces this is a geometric claim because it concerns the

\[00:12:49\] shape of the internal manifold it asks whether different behaviors are being embedded into the same region pushed apart into

\[00:12:57\] different regions or routed through distinct but related directions a network is not only a function approximator it's also a

\[00:13:06\] space organizer once you see that you realize why scale is not enough increasing the size of an entangled space

\[00:13:15\] does not automatically make it well structured a larger tangled room is still entangled geometric structure is about giving that

\[00:13:25\] room a layout why this suggests magnitude level gains most optimization tweaks produce incremental effects tiny gains benchmark noise cosmetic

\[00:13:39\] improvements but organization can create step changes why because bad structure does not merely reduce efficiency it creates systematic self-conlict

\[00:13:51\] it causes the model to spend its capacity fighting itself once that conflict is reduced improvements can appear disproportionate to

\[00:14:01\] the size of the architectural change that's why structure versus scale framing matters so much if performance ceilings are increasingly

\[00:14:10\] determined by internal interference then the next magnitude level gains may not come primarily from adding more parameters they may

\[00:14:19\] come from learning how to partition route and geometrically organize intelligence inside of the model that would be a very

\[00:14:29\] different future for AI design instead of only asking how much larger to grow the manifold we would ask how

\[00:14:37\] to shape it and then to me the bottom line within this is very simp the very simplistic framing within

\[00:14:43\] this is that so to me uh all of these models have been scaled up to the moon right uh

\[00:14:50\] claude gro like all of the current deepseek etc all the current models right and then they they've been scaled

\[00:14:56\] to the moon and they they have been scaled with all of the data uh and then so now it's

\[00:15:01\] like well what do we do from there to scale more and to scale harder and to continue scaling and

\[00:15:07\] then for me I'm saying well like you've already scaled to the moon just take advantage of that scale that

\[00:15:14\] already exists just you know like like literally use the same exact architecture that you have uh and then just

\[00:15:21\] apply it like uh more structurally literally uh and you'll get magnitudinal gains out of the same parameter performance and

\[00:15:29\] then so uh that's all it is overall right it seems pretty straightforward to me so the deeper implication this

\[00:15:37\] is about more than one experiment the broader implication is is that intelligence may depend less on raw size than

\[00:15:44\] on the quality of internal differentiation a system becomes more capable when it can preserve distinct modes without collapsing them

\[00:15:52\] together route different demands through different internal pathways avoid representational interference and maintain coherence under conflicting objectives those are architectural

\[00:16:03\] properties not just scale properties and if that is true then the industry's obsession with brute force growth may eventually

\[00:16:11\] look incomplete not wrong but incomplete scale can buy breadth structure may buy clarity scale can buy approximation structure may

\[00:16:23\] buy organization scale can buy more structure may buy better what a fair conclusion looks like a fair conclusion is

\[00:16:33\] not scale is dead that would be lazy and false a fair conclusion is this in low conflict settings scale

\[00:16:42\] can remain competitive on some headline metrics but in multitask settings where internal interference matters geometric structure can outperform pure

\[00:16:52\] scaling on the metrics that most directly reflect solution quality which are loss calibration reliability and representational separation and in

\[00:17:02\] our harder regime the case became even stronger when conflict arises structural organization becomes more impair important while scale without

\[00:17:12\] structure can fail dramatically and that's a publishable idea in and of itself not because it proves a universal law

\[00:17:20\] but because it points at a real fault line in current model design as a final thought the most important

\[00:17:27\] lesson from these experiments is simple a model can fail not because it is too small but because it is

\[00:17:33\] too entangled that is a different diagnosis and it implies a different cure pure scale asks for more mass geometric

\[00:17:43\] structure asks for better form if the future of AI depends on reducing internal conflict then form may matter more

\[00:17:52\] than mass far more often than we've been willing to admit and if that's true then the next major gains

\[00:17:59\] in intelligence may come not from building bigger minds but from building minds with cleaner geometry diving into the the

\[00:18:10\] code specifically here i'll give you like access to the full code notebook um if you want to look this

\[00:18:14\] over but uh I liked the the PowerPoint um that I did the other day and then so I have

\[00:18:19\] a PowerPoint specifically going over u these results right and so I'll give you access to to the collab notebook

\[00:18:26\] but I'll I want to go over it this way and so uh structure versus scale why organization can deliver

\[00:18:32\] disproportionate gains on a task conflict problems utilizing the same backbone plus routing plus geometric separation beats a four times

\[00:18:40\] larger shared baseline under harder conflict we run this for three runs and as far as the headline metrics we

\[00:18:48\] can reduce loss by 20 about 29% uh versus the like the large model the four time larger model um

\[00:18:56\] we reduce separation was like n above 95% like to to near zero uh and then uh we improve uh

\[00:19:04\] sentiment accuracy overall by about two point about 3% three points the thesis is that scale adds capacity while structure

\[00:19:13\] allocates it our experiments isolate the difference between more parameters and better organization for the structure first model it was

\[00:19:22\] a small same we use the same small backbone task specific routing and representation separation separation and conflict conflicts were

\[00:19:30\] handled inside of the network what the experiment showed was that when task conflict is mild both can compete but

\[00:19:36\] when conflict hardens the shared larger model collapses first that's this to me is the important takeaway within this and

\[00:19:43\] I I'm going to show this showcase this to you within the the the results here in a couple of

\[00:19:47\] slides right where uh it's the like the more overlap that you have the larger mo it impacts the larger

\[00:19:55\] model more than the smaller model and then so the core claim is that meaningful gain comes from organization and

\[00:20:02\] not just count this is just the full setup of the experimental design all of the parameters of the model

\[00:20:07\] overall uh the models uh and then the regimes framework etc and then these are the the um starting to

\[00:20:16\] go into the results right and then so this is the phase one experiment uh where we essentially we go

\[00:20:21\] over the um results in in different benchmarks first of all geometry small like absolutely slaughters everything else with regards

\[00:20:28\] towards the validation loss validation accuracy it's the only one that maintains consistent 100% accuracy once it's trained and learned

\[00:20:36\] you start to you see that that collapse start to occur with the bigger baseline right it's the very first

\[00:20:40\] one to collapse under this particular instance because of the representation overlap you can see that within this there's like

\[00:20:49\] 100% overlap uh within the representations between of the bigger baseline model uh and then with the geometry small it's

\[00:20:58\] the only one that it reduces it to literally like almost zero right um and then same thing here uh

\[00:21:05\] when we add the the other models um and then like do like the secondary test on the harder results

\[00:21:12\] same thing overall the the the um uh the uh red here is the in this particular one is the

\[00:21:19\] geometry small model uh and then it's uh getting it's the most consistent and and best loss also too like

\[00:21:26\] the adapter only small is performant is very performant within this but it doesn't beat out in the end and

\[00:21:31\] and throughout the the whole entire test the the geometry small and then especially you can see exactly why here

\[00:21:37\] because of the separations right so just by adding the adapter only small you do get some separation within this

\[00:21:44\] and then so to me that's like like the I' mentioned it a lot at this point right but like

\[00:21:49\] the JP Morgan Chase paper and a few of the other recent papers that I've gone over within this channel

\[00:21:54\] where they like they're they've discovered that this geometry exists and then they're essentially performing this like the the the

\[00:22:02\] uh uh like what I'm doing with the like uh adapter only small right where like essentially they're like um

\[00:22:10\] accounting for it and then essentially like adding another metric beyond just SGD that's and then so you can see

\[00:22:15\] just doing that alone decre like it decreases representation ation overlap which is good right like this like representation overlap

\[00:22:23\] the lower the number the better so 1.0 is a very bad number zero is a very good number uh

\[00:22:28\] and then you can see here that uh within like with the adapter only it like it's it's able to

\[00:22:33\] to train it down but it it levels off right like so it's like uh it's able to train it

\[00:22:38\] down like a good about like like it so it starts off like 20 points and then it's able to

\[00:22:42\] reduce it about 20 points below that we'll call it so like uh it's like 20 30 points cuz it

\[00:22:48\] gets down to like we'll call it like 50 um is like um 50% overlap still in existence there which

\[00:22:54\] explains like why it's not performant later on the loss here right whereas the geometry small is very performant there

\[00:23:02\] and then this is um just on the hard conflict task specifically uh and then on this one you can

\[00:23:07\] see here that geometry small is the only one that achieves that perfect baseline result uh once like like uh

\[00:23:14\] once the structure is is uh found right is is uh locked in uh it's the only one and then

\[00:23:20\] you can see that the very first one to collapse within this the worst collapses happen with the bigger baseline

\[00:23:26\] and the bigger baseline it like it it shoots up accuracy very high right um and but adapter only small

\[00:23:31\] actually beats it out but like but it but it's accur like it shoots there and then it it's the

\[00:23:36\] first and and the biggest collapses um and then same metrics that apply out within this with regards towards that

\[00:23:42\] representation overlap uh and then in this in in this particular one I would say that like adapter only small

\[00:23:48\] wins in this particular test and then second would be the the geometry aware adapter uh in my mind like

\[00:23:54\] that that like this the adapter after only small line is is super clean on this one uh and it

\[00:23:59\] could just be that particular test overall but uh essentially what's publishable within this the strong claim is is that

\[00:24:06\] in a controlled multitask interference interference benchmark a small geometry aware model matched or beat a much larger shared representation

\[00:24:14\] baseline on the outcomes that matter most under conflict test loss calibration representation separation and robustness a careful claim is

\[00:24:23\] is that the gains are not universal raw topline wins on every metric in every regime the contribution is that

\[00:24:30\] organization becomes the decisive lever as interference hardens meaning that like the bigger the model gets the more data size

\[00:24:37\] data set that you have the more noise that's within it everything that comes with scaling right like this so

\[00:24:43\] uh the more that you want to scale the more that you need this geometric structure as a design principle

\[00:24:49\] if the bottleneck is a shared representation conflict more parameters mostly enlarge the problem routing and separation make the capacity

\[00:24:57\] usable uh publishable framing is is that structure gives outsiz gains because it changes where computation happens and not just

\[00:25:05\] how much exists uh and then uh over here again I'll leave you access to all the code here which

\[00:25:11\] you can go through check it out and run and then this is where all those um graphs that we're

\[00:25:16\] looking at within that PowerPoint come from so you can get access to all of those as well as all

\[00:25:20\] the benchmark numbers uh here this is just pure benchmark testing right that's all all we're doing within here uh

\[00:25:25\] if you need a description of the notebook I give you clean uh exact a full overall description uh as

\[00:25:30\] to exactly what's going on within this point of this overall is very specifically to benchmark and prove out this

\[00:25:36\] right geometric structure beats out pure scaling on uh every single test that we do within this and it only

\[00:25:43\] becomes bigger like a a uh more and more improvement for a geometric structure the more that you want to

\[00:25:50\] scale and that's kind of just how it shakes out i didn't do it if you like this type of

\[00:25:53\] content please like and subscribe thank you very much