## Persona

# Persona is meant to represent an individual a sales rep or hr rep or agent.
# basically someone predictable and that's why I'm leaning towards
# microsoft/dialogpt-medium

from personaGPTBot import Message, PersonaGPTBot

pg = PersonaGPTBot({'Alice':["I'm a french girl","I love art","my name is Alice"],"Bob" :["I'm a french boy","I love art","my name is Bob"]},deterministic=False)

dia = []
# res = [Message(persona='Bob',text='Have you Heard? I\'m getting married!')]
res = [Message(persona='Bob',text='hello do you like to work with computers?')]

res, dia = pg.converse(10,('Alice','Bob'),startMessage=res[-1],dialog_hx=dia)
res


res = None
old_res = None
for i in range(1):
  dia = []
  res = [Message(persona='Bob',text='')]
  res, dia = pg.converse(10,('Alice','Bob'),startMessage=res[-1],dialog_hx=dia)
  if res is not None and old_res is not None and res != old_res:
    print('old_res',old_res)
    print('res',res)
  else:
    print(f'test {i} passed!')
  old_res = res
  
  a = """[Message(persona='Alice', text='hi how are you doing'),
 Message(persona='Bob', text="i'm good thanks for asking"),
 Message(persona='Alice', text='what do you do for a living'),
 Message(persona='Bob', text='i am a french boy'),
 Message(persona='Alice', text='do you have any hobbies'),
 Message(persona='Bob', text='i like to play sports'),
 Message(persona='Alice', text='what do you like about sports'),
 Message(persona='Bob', text="they're fun to play"),
 Message(persona='Alice', text='do you play often then'),
 Message(persona='Bob', text='yeah i play soccer a lot')]"""
 
 
ctx = """I think both myself and a lot of my coworkers/friends fall under this category of "backend non web-dev stack agnostic generalist software engineer" that seem to hang out in product companies.While I've gotten experience in domains by virtue of the teams and projects I've worked with, I wouldn't really identify them as being my "specialty". I've also never really identified with my tech stack, both because it changes a lot and because frankly the complexity of my work never seems to boil down to low level implementation expertise. There are almost never any serious design meetings where the main point of contention is anything that is on the layer of programming patterns or language details (but obviously yes to system design). The problems that I mainly solve seem to be more "engineering" than programming, and while I'd say they are complex, they seem to be mostly a function of general analytical reasoning and more system design-level understanding.Is this sort of position actually that common outside of tech companies? I'm asking mostly out of curiosity, but also while I was lucky to land in another tech company after getting laid off in January, if I get laid off again and don't have the same luck, I'm not sure if I should take steps to brand myself as something less generalist when exploring other options."""
 
 # pg.ask("""ask about sports""",[])
pg.ask(f"""ask about this web backends""",[])

# pg.reply("hello i'm mary and yes i've a daughter. do you have any children?","Bob", [[31373, 466, 345, 423, 597, 1751, 286, 534, 898, 30, 50256]])
pg.reply(ctx,"Bob", [[31373, 466, 345, 423, 597, 1751, 286, 534, 898, 30, 50256]])