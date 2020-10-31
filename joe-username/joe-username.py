import random

JOE_WORDS = ["right", "awesome", "interesting", "cool","cool"]
def generate(lim:int=4):
  word = ""
  for i in range(lim):
    rand_word = random.choice(JOE_WORDS)
    word += rand_word.title()
  print(f'--> {word}')
  return word

with open("README.md") as f:
  fl = f.readlines()
  i1 = fl.index('<!--username:START-->\n')
  i2 = fl.index('<!--username:END-->\n')
  
  user_name = generate(random.randint(3,11)) + '\n'
  fl = fl[:i1+1] + [user_name] + fl[i2:]
  print('--> Writing to README')
open("README.md",'w').writelines(fl)
print('--> Finished with joe-username.py')
