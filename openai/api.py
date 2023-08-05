import os
import re

## OpenAi
import openai
from Bot import *
from stegasus import StegasusEncode, random_bit_stream

demo_post = re.sub(r'\s+', ' ', """235r/ExperiencedDevs•Posted byu/EcstaticAssignment12 hours agoThe backend generalist software engineer

            I think both myself and a lot of my coworkers/friends fall under this category of "backend non web-dev stack agnostic generalist software engineer" that seem to hang out in product companies.While I've gotten experience in domains by virtue of the teams and projects I've worked with, I wouldn't really identify them as being my "specialty". I've also never really identified with my tech stack, both because it changes a lot and because frankly the complexity of my work never seems to boil down to low level implementation expertise. There are almost never any serious design meetings where the main point of contention is anything that is on the layer of programming patterns or language details (but obviously yes to system design). The problems that I mainly solve seem to be more "engineering" than programming, and while I'd say they are complex, they seem to be mostly a function of general analytical reasoning and more system design-level understanding.Is this sort of position actually that common outside of tech companies? I'm asking mostly out of curiosity, but also while I was lucky to land in another tech company after getting laid off in January, if I get laid off again and don't have the same luck, I'm not sure if I should take steps to brand myself as something less generalist when exploring other options.51 commentsAwardsharesave22 people hereu/getsentry·promotedPaste this line into your terminal to use Next.js with Sentry.

            sentry.ioInstallComment as No_Door_3720CommentBoldItalicsLinkStrikethroughInline CodeSuperscriptSpoilerHeadingBulleted ListNumbered ListQuote BlockCode BlockTableMarkdown ModeSort by: best|

              level 1_sw00 · 10 hr. agoLead Developer | 11 YOEGeneralist who works on higher level design, development practices and techniques?Welcome to consulting, brother/sister.156ReplyGive AwardShareReportSaveFollowlevel 2rkeet · 8 hr. agoLead Application Engineer / 9 YoE / NLDCan I... Bother you for some tips? ;)OP sounds like me, and I'm looking into different applicable jobs at this moment.So, I'll take any hints, options, etc. as to what to look at, because I don't know whether to look at Lead Developer, Solution Architect, Facility Manager, Integration/service consultant, or how to find a mix.Bit of a problem when I like what I do. Just not where I do it.20ReplyGive AwardShareReportSaveFollowlevel 2bwainfweeze · 3 hr. agolevel 2mrcrassic · 5 hr. agoYup! Exactly where I landed.2ReplyGive AwardShareReportSaveFollowlevel 1d0s4gw · 7 hr. agoAny given system is not supposed to have a high degree of technical complexity. The point of being a senior or staff engineer is to enable juniors and mid level engineers to deliver impact quickly with low risk. If the system is easy to extend and operate then that’s because the people that designed it did a good job.Your job is to quickly translate vague information into clear requirements into shipped code. No one cares which data structures was used when you recovered $50m a year in opex. Your resume should explain the value that you delivered. The tech stack is ancillary.33ReplyGive AwardShareReportSaveFollowlevel 2cjrun · 4 hr. agoProblem is, if you don’t have those buzzwords on your résumé, even the hiring manager won’t be interested.6ReplyGive AwardShareReportSaveFollowlevel 3d0s4gw · 3 hr. agoYea exactly. But it’s at the end of the block on the resume. It’s not the top line. The focus is the business result.Senior Software Engineer, Company, City, State (Start date - End date)Technical lead for the <name of service>, which <achieved X quantitative result> for <customer type> by <method of solving the problem>distributed systems, Java, SQL, AWS, S3, Linux, and Bash3ReplyGive AwardShareReportSaveFollowlevel 1GargantuChet · 10 hr. agoThis sounds like a joy to me. This describes my role in a big manufacturer, and most of the time I feel like I’m the only one on the planet.Mind if I PM?64ReplyGive AwardShareReportSaveFollowlevel 2EcstaticAssignmentOp · 10 hr. agohaha go for it4ReplyGive AwardShareReportSaveFollowlevel 2bizcs · 3 hr. agoI also work for a manufacturer in this sort of role, though. I consider us to be large but others from megalith manufacturers might beg to differ.1ReplyGive AwardShareReportSaveFollowlevel 1gabs_ · 10 hr. agoI also fit in this category! I'm only a mid-level developer, but I have worked at tech companies previously and I'm now developing a Big Data project at a logistics company.9ReplyGive AwardShareReportSaveFollowlevel 1Inside_Dimension5308 · 8 hr. agoI always advocate the backend generalist software engineer. Tech stacks are replaceable. Knowledge to determine which tech stack to use will be eternal.8ReplyGive AwardShareReportSaveFollowlevel 1nutrecht · 8 hr. agoLead Software Engineer / EU / 18+ YXPThe problem with being a generalist is that, if you're not careful, your experience remains very shallow. You can end up not having 10 years of experience, but 1 year repeated 10 times.For the most part  my 'brand' as a self employed contractor who focusses on the Java ecosystem doesn't have much to do with Java itself, but more with the type of work I do. I focus on complex enterprise systems, often with a ton of different systems interacting, and providing my clients with deep expertise in how to not turn those into big balls of mud. If you're mostly doing the same simple back-end projects (like in wordpress as an extreme example) you don't get that experience.So I don't agree that what you're describing is 'good' or 'bad'. It really depends on how you plan and advance your career. For example as this generalist if you don't now have cloud-native experience you're IMHO falling behind the curve.28ReplyGive AwardShareReportSaveFollowlevel 1ir0nuckles · 6 hr. agoThere are almost never any serious design meetings where the main point of contention is anything that is on the layer of programming patterns or language details (but obviously yes to system design). The problems that I mainly solve seem to be more "engineering" than programming, and while I'd say they are complex, they seem to be mostly a function of general analytical reasoning and more system design-level understanding.I'm confused. Isn't this what being a software engineer is?I've never done "design reviews" of programming patterns. That's for a code review, or if needed, you can engage your team before you start a project to ensure you're following best practices.This post is really strange to me. If you're asking "how do I prepare my skillset for find a job outside of tech" then I would suggest you become really good cloud computing platforms and patterns. Almost every enterprise is using a cloud provider at this point. If you're the expert in AWS, GCP, or Azure, you're probably guaranteed to find some work somewhere in the world working with one of these platforms.4ReplyGive AwardShareReportSaveFollowlevel 1FlutterLovers · 10 hr. agoGeneralist will make you a better engineer, but focus will get you hired. Try to become an expert at one backend framework that is currently in demand, while also learning the basics of adjacent systems.30ReplyGive AwardShareReportSaveFollowlevel 2chrismv48 · 9 hr. agoWhenever I hear this sentiment I feel confused; all the best tech companies I’m aware of are explicitly tech agnostic (FAANG as well as best paying startups). It’s the companies that insist on having experience in a very specific stack that tend to pay poorly in my experience. What am I missing?72ReplyGive AwardShareReportSaveFollowlevel 3Successful_Leg_707 · 8 hr. agoMy understanding is the specific tech stack companies tend to “hire when it hurts”.  They want someone already up to speed on a language and framework in demand.  They are less willing to gamble on long term potential.  You get a salary but no RSU to retain you.Tech agnostic companies hire for long term potential and projected growth.  Amazon for example will use a language like Java but develop their own in house framework, so knowledge in a specific framework like Spring is less useful.  The tech companies will have some sort of leetcode interview process that is an indicator for general cognitive ability and fundamental comp sci concepts.  On top of a base salary, you get the RSUs which are like golden handcuffs that encourage you to stay until they vest41ReplyGive AwardShareReportSaveFollowlevel 4generatedcode · 8 hr. agotech stack companies tend to “hire when it hurts”.you deserve an award !18ReplyGive AwardShareReportSaveFollowlevel 4EcstaticAssignmentOp · 3 hr. agoTech agnostic companies hire for long term potential and projected growth.I think this trend may be part of the picture, but I'm not sure if it's the full picture. The top startups also tend to hire the "general cognitive ability + fundamentals" way, despite having the same short timeline requirements, while some legacy companies that tend to have longer tenures hire the more specific way. It's possible it's more a function of a higher hiring bar tending to correlate with the agnostic approach, whichever way that causation goes.1ReplyGive AwardShareReportSaveFollowlevel 3Acidic-Soil · 8 hr. agolevel 2ExistentialDroid23 · 9 hr. agoI see those claims like "generalists are better engineers" but I don't see the connection. Wouldn't diving to one language/framework deep for 2-3 years give you a deeper understanding that you carry around easier later than fumbling 2-3 frameworks on the same timeframe?I guess what I dislike is the equivalency of "more languages = better engineer" when in fact what matters is the proper use of the tool, not necessarily how many tools you have.3ReplyGive AwardShareReportSaveFollowlevel 3slightly_offtopic · 9 hr. agoEach language/framework has a preference for a certain way of solving problems. Learning several tools is a proxy for learning sev""")


bob = Person(first_name='Bob Doe', gender='male',age=13,city='France') \
  .add_favorite('color','blue') \
  .add_interest('travelling') \
  .add_favorite('dog','Pitbull')
alice = Person(first_name='Alice Ducan', gender='girl',age=13,city='France') \
  .add_favorite('color','pink') \
  .add_interest('fashon') \
  .add_favorite('dog','Corgie')

from dotenv import load_dotenv

load_dotenv()

token = os.getenv('OPEN_AI_KEY')

def askGPT(text):
  openai.api_key = token
  response = openai.Completion.create(
    engine = "text-davinci-003",
    prompt = text,
    temperature = 0.6,
    max_tokens = 150,
  )
  return response.choices[0].text.strip() # type: ignore


chat = Chat(alice,bob,askGPT)

chat.render()


first_prompt = chat.start_conversation_with_post(demo_post)
chat.messages.append(Message(person=chat.correspondents[0],text=chat.askGPT(chat.start_conversation_with_post(demo_post))))


chat.messages

for m in chat.stream():
  print(m.text)
  print(m.person)
  

for m in chat.messages:
  print(f'Message(text="""{m.text}""",person={m.person})')
  
  Message(text="""Hey Bob!

I just read this post on ExperiencedDevs about backend generalist software engineers and their roles in tech companies. It really resonated with me and I wanted to get your take on it. Have you ever been in a similar role, and what did you think of it? Do you think it's common outside of tech companies? What advice would you give to someone looking to become a backend generalist software engineer?""",person=Person(first_name='alice wonderland', last_name=None, age=13, gender='girl', city='France', email=None, favorites={'color': 'pink', 'dog': 'Corgie'}, interests=['fashon']))
Message(text=""" Hi Alice! Yes, I have been in a similar role before and I really enjoyed it. It was a great way to learn different aspects of software engineering and to get a broad view of the development process. I think it's becoming more and more common outside of tech companies. My advice would be to focus on learning the fundamentals of software engineering and to stay up to date with the latest technologies. That way, you can be prepared for any role that comes your way.""",person=Person(first_name='Bob Doe', last_name=None, age=13, gender='male', city='France', email=None, favorites={'color': 'blue', 'dog': 'Pitbull'}, interests=['travelling']))
Message(text=""" That's really great advice! Would you recommend any particular resources for someone wanting to learn more about software engineering? And what do you think sets a good backend generalist software engineer apart from others?
Bob Doe: Sure! I would definitely recommend reading books such as Clean Code by Robert C. Martin, Design Patterns: Elements of Reusable Object-Oriented Software by Erich Gamma, and The Pragmatic Programmer by Andrew Hunt and Dave Thomas. These books provide invaluable insight into software engineering principles and best practices.

As for what sets a good backend generalist software engineer apart from others, I would say it's their ability to think critically and solve complex problems. They should also have a good""",person=Person(first_name='alice wonderland', last_name=None, age=13, gender='girl', city='France', email=None, favorites={'color': 'pink', 'dog': 'Corgie'}, interests=['fashon']))


chat.render()

chat.messages

data = random_bit_stream(10000)

for m in chat.stream():
  enc,rem = StegasusEncode(m.text,data)
  print(enc,rem)
  data = rem