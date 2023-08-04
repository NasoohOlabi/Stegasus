from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Tuple
import torch
from dataclasses import dataclass


ACTION_SPACE = [ 'ask about kids.', "ask about pets.", 'talk about work.',
               'ask about marital status.', 'talk about travel.', 'ask about age and gender.',
        'ask about hobbies.', 'ask about favorite food.', 'talk about movies.',
        'talk about music.', 'talk about politics.']

@dataclass
class Message:
    persona: str
    text: str

class PersonaGPTBot:

    def __init__(self, personas:Dict[str, List[str]], action_space=ACTION_SPACE, model_name="af1tang/personaGPT", use_fast=False,deterministic = True):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=use_fast)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        if torch.cuda.is_available():
            self.model = self.model.cuda()
        if 'Bot' not in personas:
          personas['Bot'] = ["My name is RobotMan","I used to be called cliff steel","I was a Nascar Racer"]
        self.personas = dict()
        for k,v in personas.items():
          self.personas[k] = self.tokenizer.encode(''.join(['<|p2|>'] + v + ['<|sep|>'] + ['<|start|>']))
        self.action_space = action_space
        self.dialog_hx = []
        self.deterministic = deterministic

    def flatten(self, l):
        return [item for sublist in l for item in sublist]

    def to_data(self, x):
        if torch.cuda.is_available():
            x = x.cpu()
        return x.data.numpy()

    def to_var(self, x):
        if not torch.is_tensor(x):
            x = torch.Tensor(x)
        if torch.cuda.is_available():
            x = x.cuda()
        return x

    def generate_next(self,
                  bot_input_ids,
                  ):
        if not self.deterministic:
            do_sample=True
            top_k=10
            top_p=.6
            temperature=0.5
        else:
            do_sample=False
            top_k=10
            top_p=.6
            temperature=1e-5
        max_length=1000 # Maximum length of generated message
        pad_token = self.tokenizer.eos_token_id

        # Generate a full message using the provided model and parameters
        full_msg = self.model.generate(
            bot_input_ids,
            do_sample=do_sample,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            max_length=max_length,
            pad_token_id=self.tokenizer.eos_token_id
        )

        # Extract the message from the full generated output and return it
        msg = self.to_data(full_msg.detach()[0])[bot_input_ids.shape[-1]:]
        return msg


    def reply(self,user_input,persona:str = "Bot",dialog_hx=None):
        # respond to input
        dialog_hx= dialog_hx if dialog_hx is not None else self.dialog_hx

        # encode the user input
        user_inp = self.tokenizer.encode(user_input + self.tokenizer.eos_token)
        # append to the chat history
        dialog_hx.append(user_inp)

        # generate a response while limiting the total chat history to 1000 tokens
        bot_input_ids = self.to_var([self.personas[persona] + self.flatten(dialog_hx)]).long()
        msg = self.generate_next(bot_input_ids)
        response = self.tokenizer.decode(msg, skip_special_tokens=True)

        return response, dialog_hx

    def ask(self,action:str,dialog_hx=None):
        # respond to input
        if isinstance(action, int):
          action = self.action_space[action]
        dialog_hx= dialog_hx if dialog_hx is not None else self.dialog_hx
        action_prefix = self.tokenizer.encode(f'<|act|>{action}<|p1|><|sep|><|start|>')
        bot_input_ids = self.to_var([action_prefix + self.flatten(dialog_hx)]).long()

        # generate query conditioned on action
        msg = self.generate_next(bot_input_ids)

        query = self.tokenizer.decode(msg, skip_special_tokens=True)

        return query, dialog_hx

    def resume_chat(self, dialog_hx):
        self.dialog_hx = dialog_hx

    def converse(self,length, personas:Tuple[str,str], action=None, startMessage:Message=None, dialog_hx=None):
        dialog_hx= dialog_hx if dialog_hx is not None else self.dialog_hx
        if action is None and startMessage is None:
          startMessage = Message(persona=personas[0],text='')
        res = ''
        responses = []
        if action is not None:
          res, dialog_hx = self.ask(action,dialog_hx)
        else:
          res, dialog_hx = self.reply(startMessage.text,startMessage.persona,dialog_hx)
        responses.append(Message(text=res,persona=personas[0]))
        turn = 1
        for i in range(length-1):
          res, dialog_hx = self.reply(res,personas[turn],dialog_hx)
          responses.append(Message(text=res,persona=personas[turn]))
          turn = (turn+1) % 2

        return responses , dialog_hx
