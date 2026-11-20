import random
print("Я загадал число от 1 до 10.Попробуй угадать!")
secret_number = random.randint(1,10)
is_guessed = False
while is_guessed == False:
    guess = int(input("Твой вариант: "))
    if guess > secret_number:
        print("Моё число меньше!")
    elif guess> secret_number:
        print("Моё число больше!")
    else:
        print("Ты угадал!")
        is_guessed = True
 