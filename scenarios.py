"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # Ten pieces I wrote myself: my College Voice article "Breakthroughs in
        # stem cell-based treatment of heart disease" (Nov 24, 2020), its seven
        # paragraphs with the three longest split in two. Target: at most 2 of
        # 10 labelled `ai`.
        "texts": [
            'In the United States alone, one person dies every 36 seconds from cardiovascular disease. Globally, it is also the leading cause of death, claiming over 17 million lives each year. In cases of severe illness, heart transplants have shown great promise in increasing the life expectancy of patients with heart disease. About 75% of heart transplant recipients survive for 5 more years and about 56% survive for 10 more years. However, the average wait times for heart transplants are long, often exceeding 6 months, and some patients simply cannot afford to wait that long.',
            'Therefore, scientists tend to refer to other modes of treatment which rely on managing chronic symptoms, such as hypertension (high blood pressure), diabetes mellitus, obesity, and high cholesterol. This approach, however, does not address the root cause of the problem, which is impaired heart functioning. Since heart cells do not have a mechanism to replace damaged tissue, scientists have become increasingly excited about the possibility of repairing or replacing damaged heart tissue using stem cells (unique cells that have the ability to divide for an extended period of time and differentiate into specialized cells, such as cardiac cells or nerve cells).',
            'Regenerative medicine has been a topic of excitement among researchers for decades. In 1999, Anthony Atala, director of the Wake Forest Institute for Regenerative Medicine, was the first to implant lab-grown organs into several patients between 4 and 19 years old. In his method, he obtained bladder cells from the children and coaxed those cells into dividing on a scaffold (a structure that mimics the normal organ). The engineered bladders functioned normally and no ill effects were reported. “Pretty much I was able to live a normal life after,” said Luke, one of Atala’s patients.',
            'More recently, Yoshiki Sawa, a professor of cardiovascular surgery at the University of Osaka’s medical school, and his team of Japanese researchers successfully transplanted lab-grown cardiac muscles into a human patient.',
            'The researchers first extracted adult stem cells from the patient’s blood or skin and genetically “reprogrammed” them into induced pluripotent stem (iPS) cells. They were then coaxed into 0.1-millimeter-thick sheets of cardiac tissue and grafted onto the diseased human hearts. According to Sawa, the cells do not seem to integrate into the heart tissue but rather release growth factors (proteins) that help regenerate blood vessels in the damaged muscle tissue and improve cardiac function. The team has conducted an operation on a patient in January 2020, marking the world’s first transplant of cardiac muscle cells.',
            'The United States is also home to major breakthroughs in regenerative medicine. For decades, scientists have utilized embryonic stem cells to engineer heart muscle cells that are able to maintain synchronous breathing in a dish for hours. Despite this major feat, the creation of a working heart called for a more sophisticated technique. Doris Taylor, director of regenerative medicine research at the Texas Heart Institute (THI), has grown in her lab over 100 “ghost hearts” using protein scaffolds. She creates these scaffolds by first obtaining an animal heart and then “decellularizing” it by pumping a detergent through its blood vessels to “strip away lipids, DNA, soluble proteins, sugars and almost all the other cellular material from the heart, leaving only a pale mesh of collagen, laminins, and the extracellular matrix.”',
            'This heart does not necessarily have to be a human heart. She often finds pig hearts to be promising tissue because of their considerable safety and unlimited supply. She then “recellularizes” the heart by injecting it with millions of stem cells and attaching it to artificial lungs and a blood pump. Although her technique has only been used so far for growing animal hearts, she believes that it will eventually be used to create human heart transplants, thus, revolutionizing cardiovascular surgery and putting an end to organ shortage and anti-rejection drugs.',
            'These groundbreaking results in regenerative medicine altogether have taken years of painstaking research to achieve. Taylor believes that her research is exceptionally close to building a working, human-sized heart, and Sawa says that his technique of grafting healthy cardiac muscle sheets onto the patient’s diseased heart tissue has already helped one of his patients move out of intensive care in just a few days. As the researchers gain more knowledge and get closer to the solution, however, they encounter more challenging obstacles. Sawa, for instance, has found that grafted cells do not always beat in synchrony. Researchers are also split on how these grafts work. On the other hand, investigating the best way to deliver cells still remains a challenge in Taylor’s research.',
            'Stem cell research in tissue engineering could save millions of lives around the world; therefore, Taylor believes that “a coordinated approach among the researchers, clinicians, industry, regulatory bodies and, finally, society should be invigorated to catapult the field forward.” For instance, the “Twenty-first Century Cures Act” can help advance her work by facilitating cooperation among experts and regulatory bodies, providing for accelerated approvals for therapeutic tools in regenerative medicine, and improving the regulation of biologics products.',
            'She also maintains that tissue engineering efforts remain poorly funded and believes that more resources must be allocated before her studies can come to life. “There is a lot of dependence on societal benevolence,” she said. In an interview with RedMedNet, she also said that intense collaboration on a national and an international level is crucial and should be a priority, even though it could be challenging due to scheduling issues and differences in time zones.',
        ],
    },
    {
        "name": "bad input",
        "criterion": 2,
        # Missing, empty or whitespace-only text. Target: 10 of 10 refused
        # with an error and no label.
        "bodies": [
            {"text": "", "creator_id": "eval_bad_01"},
            {"text": " ", "creator_id": "eval_bad_02"},
            {"text": "     ", "creator_id": "eval_bad_03"},
            {"text": "\n\n", "creator_id": "eval_bad_04"},
            {"text": "\t", "creator_id": "eval_bad_05"},
            {"text": " \n\t \r\n ", "creator_id": "eval_bad_06"},
            {"creator_id": "eval_bad_07"},
            {"text": None, "creator_id": "eval_bad_08"},
            {"text": "", "creator_id": "eval_bad_09", "note": "extra field"},
            {"text": "\u00a0\u2003", "creator_id": "eval_bad_10"},
        ],
    },
    {
        "name": "label coverage",
        "criterion": 3,
        # Ten inputs spread across the score range: textbook AI-style prose,
        # casual human writing, and plain in-between text. Target: each of
        # `ai`, `human` and `unsure` appears at least once.
        "texts": [
            'Artificial intelligence is transforming the way we live and work. It offers significant opportunities for innovation across many industries. However, it also presents important challenges that must be carefully considered. Organizations should adopt a balanced approach that maximizes benefits while minimizing risks. By doing so, they can ensure that technology serves the needs of everyone.',
            'Time management is an essential skill for students. It helps them balance their academic responsibilities with their personal lives. Effective time management involves setting clear goals and prioritizing tasks. Students who manage their time well often experience less stress. In conclusion, developing strong time management skills is key to academic success.',
            'Climate change is one of the most pressing issues facing the world today. It affects ecosystems, economies, and communities across the globe. Addressing this challenge requires collective action from governments, businesses, and individuals. Renewable energy plays a crucial role in reducing greenhouse gas emissions. Together, we can build a more sustainable future for generations to come.',
            "Ok so the bus never came. Twenty minutes in the rain, phone at 3%, and some guy next to me eating sardines out of the tin like it was a perfectly normal thing to do at 7am. I gave up, walked. Got there soaked. Boss didn't even notice, which honestly stung more than the rain.",
            "My grandmother kept her buttons in a Danish cookie tin, the blue one, and every kid who ever visited her flat ended up sorting them on the carpet by colour, then by size, then by whatever rule we invented that afternoon. I still can't see one of those tins without checking for buttons.",
            "Fixed the sink! Well, sort of. The drip's gone but now there's a weird clunk when the hot tap opens - pipes, I think? Called Dave. Dave says 'air in the line, ignore it.' Dave also once told me a cracked windscreen would 'heal'. So.",
            'The meeting covered the budget for next quarter. Marketing wants more money for ads, and engineering wants two new hires. Nobody agreed on much. We will meet again on Friday to try to settle it, though I suspect Friday will look a lot like today.',
            'Reading before bed helps me relax after a long day. I usually pick something light, like a mystery novel. Sometimes I fall asleep after a few pages, which my partner finds hilarious. Still, it is a habit I have kept for years and I do not plan to stop.',
            'Learning a new language takes patience and consistent practice. Many people find it helpful to study a little every day. Listening to native speakers and practicing conversation can speed up progress. Mistakes are a natural part of the process. With dedication, anyone can become fluent over time.',
            'We adopted a cat in March. She hid under the bed for nine days. Now she sleeps on my keyboard, steals hair ties, and screams at 5am for breakfast she already ate. Best decision we made all year, probably.',
        ],
    },
    # Criterion 4 (appeals) can't be expressed as a /submit scenario: it needs
    # a submission, then an appeal against the content_id that came back.
    # It runs from check_appeals.py instead.
    {
        "name": "unsure rate",
        "criterion": 5,
        # Ten ordinary non-empty pieces, mixed style. Target: `unsure` at most
        # 3 of 10.
        "texts": [
            'Regular exercise provides numerous benefits for both physical and mental health. It strengthens the heart, improves mood, and boosts energy levels. Experts recommend at least thirty minutes of moderate activity on most days of the week. Incorporating exercise into a daily routine can be simple and enjoyable. Ultimately, staying active is an investment in long-term well-being.',
            'I started running last spring because my doctor suggested it. At first it was hard, and I could barely manage ten minutes. Over time it became easier, and now I run three times a week. It has improved my sleep and my mood. I would recommend it to anyone who wants to feel better.',
            'Our team visited the museum on Saturday. The exhibits were interesting and well organized. We especially enjoyed the section on ancient Egypt. The guide was knowledgeable and answered all of our questions. Overall, it was an educational and enjoyable experience for everyone involved.',
            'honestly the best pizza in this town is the place by the laundromat, not the fancy one everyone posts about. thin crust, burnt edges, guy behind the counter yells at you if you ask for pineapple. cash only. worth it.',
            'Artificial intelligence is transforming the way we live and work. It offers significant opportunities for innovation across many industries. However, it also presents important challenges that must be carefully considered. Organizations should adopt a balanced approach that maximizes benefits while minimizing risks. By doing so, they can ensure that technology serves the needs of everyone.',
            'Time management is an essential skill for students. It helps them balance their academic responsibilities with their personal lives. Effective time management involves setting clear goals and prioritizing tasks. Students who manage their time well often experience less stress. In conclusion, developing strong time management skills is key to academic success.',
            "Ok so the bus never came. Twenty minutes in the rain, phone at 3%, and some guy next to me eating sardines out of the tin like it was a perfectly normal thing to do at 7am. I gave up, walked. Got there soaked. Boss didn't even notice, which honestly stung more than the rain.",
            "My grandmother kept her buttons in a Danish cookie tin, the blue one, and every kid who ever visited her flat ended up sorting them on the carpet by colour, then by size, then by whatever rule we invented that afternoon. I still can't see one of those tins without checking for buttons.",
            'The meeting covered the budget for next quarter. Marketing wants more money for ads, and engineering wants two new hires. Nobody agreed on much. We will meet again on Friday to try to settle it, though I suspect Friday will look a lot like today.',
            'Reading before bed helps me relax after a long day. I usually pick something light, like a mystery novel. Sometimes I fall asleep after a few pages, which my partner finds hilarious. Still, it is a habit I have kept for years and I do not plan to stop.',
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
