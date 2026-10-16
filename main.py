import ast

import operator

import math

import re

import unicodedata

from knowledge import solve_knowledge
from reasoning import solve_reasoning



OPERATORS = {

    ast.Add: operator.add,

    ast.Sub: operator.sub,

    ast.Mult: operator.mul,

    ast.Div: operator.truediv,

    ast.FloorDiv: operator.floordiv,

    ast.Mod: operator.mod,

    ast.Pow: operator.pow,

    ast.UAdd: operator.pos,

    ast.USub: operator.neg,

}



HINDI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")



HINDI_NUMBERS = {

    "एक": "1",

    "दो": "2",

    "तीन": "3",

    "चार": "4",

    "पाँच": "5",

    "पांच": "5",

    "छह": "6",

    "छः": "6",

    "सात": "7",

    "आठ": "8",

    "नौ": "9",

    "दस": "10",

    "ग्यारह": "11",

    "बारह": "12",

    "तेरह": "13",

    "चौदह": "14",

    "पंद्रह": "15",

    "पन्द्रह": "15",

    "सोलह": "16",

    "सत्रह": "17",

    "अठारह": "18",

    "उन्नीस": "19",

    "बीस": "20",

    "तीस": "30",

    "चालीस": "40",

    "पचास": "50",

    "साठ": "60",

    "सत्तर": "70",

    "अस्सी": "80",

    "नब्बे": "90",

    "सौ": "100",

}





def normalize_question(question):

    """Hindi digits aur common number words normalize karein."""

    question = unicodedata.normalize("NFKC", question)

    question = question.translate(HINDI_DIGITS)

    question = question.strip().lower()



    for word, number in sorted(

        HINDI_NUMBERS.items(),

        key=lambda item: len(item[0]),

        reverse=True

    ):

        question = re.sub(

            rf"(?<!\w){re.escape(word)}(?!\w)",

            number,

            question

        )



    question = question.replace("।", ".")

    question = question.replace("×", "*")

    question = question.replace("÷", "/")

    question = question.replace("−", "-")



    return question





def is_hindi(question):

    return any("\u0900" <= char <= "\u097F" for char in question)





def calculate(node):

    if isinstance(node, ast.Constant):

        if type(node.value) in (int, float):

            if not math.isfinite(node.value):

                raise ValueError("Number valid nahi hai.")

            return node.value



        raise ValueError("Sirf numbers ka use karein.")



    if isinstance(node, ast.BinOp):

        left = calculate(node.left)

        right = calculate(node.right)

        operation = OPERATORS.get(type(node.op))



        if operation is None:

            raise ValueError("Operation supported nahi hai.")



        if isinstance(node.op, ast.Pow):

            if abs(right) > 100 or abs(left) > 10**10:

                raise ValueError("Power bahut badi hai.")



        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):

            if right == 0:

                raise ValueError("Zero se divide nahi kar sakte.")



        try:

            result = operation(left, right)

        except (OverflowError, ZeroDivisionError):

            raise ValueError("Calculation ka result valid nahi hai.")



        if isinstance(result, (int, float)):

            if not math.isfinite(result):

                raise ValueError("Result bahut bada hai.")



            if abs(result) > 10**100:

                raise ValueError("Result bahut bada hai.")



        return result



    if isinstance(node, ast.UnaryOp):

        operation = OPERATORS.get(type(node.op))



        if operation is None:

            raise ValueError("Operation supported nahi hai.")



        return operation(calculate(node.operand))



    raise ValueError("Sawal ka format sahi nahi hai.")





def solve_average(question):

    question = question.strip().lower()

    match = re.match(r"^(average|avg|ausat)\b", question)



    if not match:

        return None



    remaining = question[match.end():].strip()



    if not remaining:

        raise ValueError("Average nikalne ke liye numbers likhein.")



    parts = remaining.split()



    if len(parts) > 50:

        raise ValueError("Ek baar mein adhiktam 50 numbers daalein.")



    numbers = []



    for part in parts:

        if not re.fullmatch(r"[+-]?\d+(?:\.\d+)?", part):

            raise ValueError(

                "Average ke liye sirf numbers aur spaces use karein."

            )



        number = float(part)



        if not math.isfinite(number):

            raise ValueError("Number valid nahi hai.")



        numbers.append(number)



    average = math.fsum(numbers) / len(numbers)



    if not math.isfinite(average):

        raise ValueError("Average result bahut bada hai.")



    return average





def solve_hcf_lcm(question):

    question = question.strip().lower()

    match = re.match(r"^(hcf|lcm)\b", question)



    if not match:

        return None



    operation = match.group(1)

    remaining = question[match.end():].strip()

    parts = remaining.split()



    if len(parts) < 2:

        raise ValueError(

            "HCF/LCM ke liye kam se kam do integers likhein."

        )



    if len(parts) > 50:

        raise ValueError("Ek baar mein adhiktam 50 numbers daalein.")



    numbers = []



    for part in parts:

        if not re.fullmatch(r"[+-]?\d+", part):

            raise ValueError(

                "HCF/LCM ke liye sirf poore integers likhein."

            )



        number = int(part)



        if abs(number) > 10**100:

            raise ValueError("Number bahut bada hai.")



        numbers.append(abs(number))



    if operation == "hcf":

        result = 0



        for number in numbers:

            result = math.gcd(result, number)



        if result == 0:

            raise ValueError(

                "Sabhi numbers zero hain; HCF define nahi hai."

            )



        return result



    result = 1



    for number in numbers:

        if number == 0:

            return 0



        result = (result // math.gcd(result, number)) * number



        if result > 10**100:

            raise ValueError("LCM bahut bada hai.")



    return result





def solve_age(question):

    question = question.strip().lower()



    match = re.fullmatch(

        r"age\s+(\d+)\s+(\d+)\s+(\d+(?:\.\d+)?)",

        question

    )



    if not match:

        match = re.fullmatch(

            r"age\s+(\d+)\s*:\s*(\d+)\s+"

            r"(?:ka\s+)?total\s+(\d+(?:\.\d+)?)",

            question

        )



    if not match:

        return None



    first_ratio = int(match.group(1))

    second_ratio = int(match.group(2))

    total_age = float(match.group(3))



    if first_ratio == 0 and second_ratio == 0:

        raise ValueError("Dono age ratio zero nahi ho sakte.")



    if total_age <= 0 or not math.isfinite(total_age):

        raise ValueError("Total age zero se zyada honi chahiye.")



    ratio_sum = first_ratio + second_ratio



    first_age = total_age * first_ratio / ratio_sum

    second_age = total_age * second_ratio / ratio_sum



    if not math.isfinite(first_age) or not math.isfinite(second_age):

        raise ValueError("Age ka result valid nahi hai.")



    return first_age, second_age





def solve_age_difference(question):

    question = question.strip().lower()



    patterns = [

        # Hindi: do vyaktiyon ki umar ka anupat 5:3...

        (

            r"(?:दो\s+)?व्यक्तियों\s+की\s+उम्र\s+का\s+"

            r"(?:अनुपात|रेशियो|ratio)\s+"

            r"(\d+)\s*:\s*(\d+)\s+है"

            r".*?(?:उम्र|आयु)\s+में\s+"

            r"(\d+(?:\.\d+)?)\s+"

            r"(?:साल|वर्ष)\s+का\s+अंतर\s+है"

        ),



        # Hindi alternate wording:

        # Ratio 5:3 hai aur umar ka antar 12 saal hai.

        (

            r"(?:अनुपात|रेशियो|ratio)\s+"

            r"(\d+)\s*:\s*(\d+)"

            r".*?(?:उम्र|आयु)\s+का\s+अंतर\s+"

            r"(\d+(?:\.\d+)?)"

        ),



        # Roman Hindi:

        # age difference 12 ratio 5 3

        (

            r"age\s+difference\s+(\d+(?:\.\d+)?)\s+"

            r"ratio\s+(\d+)\s+(\d+)"

        ),



        # English:

        # ratio 5:3 difference 12

        (

            r"ratio\s+(\d+)\s*:\s*(\d+)\s+"

            r"difference\s+(\d+(?:\.\d+)?)"

        ),

    ]



    for index, pattern in enumerate(patterns):

        match = re.search(pattern, question)



        if not match:

            continue



        if index == 2:

            difference = float(match.group(1))

            first_ratio = int(match.group(2))

            second_ratio = int(match.group(3))

        else:

            first_ratio = int(match.group(1))

            second_ratio = int(match.group(2))

            difference = float(match.group(3))



        if first_ratio <= second_ratio:

            raise ValueError(

                "Pehle vyakti ka ratio doosre vyakti se bada hona chahiye."

            )



        if difference <= 0:

            raise ValueError("Umar ka antar zero se zyada hona chahiye.")



        ratio_difference = first_ratio - second_ratio



        first_age = difference * first_ratio / ratio_difference

        second_age = difference * second_ratio / ratio_difference



        if not all(

            math.isfinite(x) and 0 < x <= 150

            for x in (first_age, second_age)

        ):

            raise ValueError("Nikala gaya age result valid nahi hai.")



        return first_age, second_age



    return None





def solve_father_son_age(question):

    question = question.strip().lower()



    patterns = [

        # Hindi:

        # पिता की उम्र बेटे की उम्र से 4 गुना है।

        # 5 साल बाद पिता की उम्र बेटे की उम्र की 3 गुना होगी।

        (

            r"पिता\s+की\s+उम्र\s+बेटे\s+की\s+उम्र\s+"

            r"(?:से\s+)?(\d+(?:\.\d+)?)\s+गुना\s+है"

            r".*?(\d+(?:\.\d+)?)\s+"

            r"(?:साल|वर्ष)\s+बाद\s+"

            r"पिता\s+की\s+उम्र\s+बेटे\s+की\s+उम्र\s+"

            r"की\s+(\d+(?:\.\d+)?)\s+गुना"

        ),



        # Alternate Hindi wording

        (

            r"पिता\s+(\d+(?:\.\d+)?)\s+गुना\s+"

            r"(?:बड़े|बड़ा)\s+हैं?"

            r".*?(\d+(?:\.\d+)?)\s+"

            r"(?:साल|वर्ष)\s+बाद.*?"

            r"(\d+(?:\.\d+)?)\s+गुना"

        ),



        # Roman Hindi:

        # father son 4 future 5 3

        (

            r"father\s+son\s+"

            r"(\d+(?:\.\d+)?)\s+future\s+"

            r"(\d+(?:\.\d+)?)\s+"

            r"(\d+(?:\.\d+)?)"

        ),

    ]



    match = None



    for pattern in patterns:

        match = re.search(pattern, question)



        if match:

            break



    if not match:

        return None



    current_ratio = float(match.group(1))

    years_later = float(match.group(2))

    future_ratio = float(match.group(3))



    if not all(

        math.isfinite(x)

        for x in (current_ratio, years_later, future_ratio)

    ):

        raise ValueError("Numbers valid hone chahiye.")



    if current_ratio <= 1 or future_ratio <= 0:

        raise ValueError("Age ratios valid hone chahiye.")



    if years_later < 0 or years_later > 150:

        raise ValueError("Years ki value valid honi chahiye.")



    denominator = current_ratio - future_ratio



    if denominator == 0:

        raise ValueError(

            "Di gayi conditions se ek unique age answer nahi nikalta."

        )



    son_age = (

        (future_ratio - 1) * years_later / denominator

    )



    father_age = current_ratio * son_age



    if not all(

        math.isfinite(x) and 0 < x <= 150

        for x in (son_age, father_age)

    ):

        raise ValueError(

            "Di gayi conditions se valid age answer nahi nikalta."

        )



    if son_age >= father_age:

        raise ValueError("Father ki umar son se zyada honi chahiye.")



    if not math.isclose(

        father_age + years_later,

        future_ratio * (son_age + years_later),

        rel_tol=1e-9,

        abs_tol=1e-9

    ):

        raise ValueError(

            "Di gayi conditions aapas mein match nahi karti."

        )



    return father_age, son_age





def solve_percentage(question):

    question = question.strip().lower()

    question = question.replace("का", "ka")



    match = re.fullmatch(

        r"(-?\d+(?:\.\d+)?)\s+me\s+"

        r"(-?\d+(?:\.\d+)?)\s*%\s*"

        r"(?:badhao|badhaao|badhaye|increase|barhao)",

        question

    )



    if match:

        number = float(match.group(1))

        percent = float(match.group(2))



        if percent < 0:

            raise ValueError("Percentage negative nahi honi chahiye.")



        return number + number * percent / 100



    match = re.fullmatch(

        r"(-?\d+(?:\.\d+)?)\s+me\s+"

        r"(-?\d+(?:\.\d+)?)\s*%\s*"

        r"(?:ghatao|ghataayo|ghatayo|kam karo|decrease)",

        question

    )



    if match:

        number = float(match.group(1))

        percent = float(match.group(2))



        if percent < 0:

            raise ValueError("Percentage negative nahi honi chahiye.")



        return number - number * percent / 100



    match = re.fullmatch(

        r"(-?\d+(?:\.\d+)?)\s+(?:par|per)\s+"

        r"(-?\d+(?:\.\d+)?)\s*%\s*"

        r"(?:chhoot|chut|discount|off)",

        question

    )



    if match:

        number = float(match.group(1))

        percent = float(match.group(2))



        if number < 0:

            raise ValueError("Price negative nahi ho sakti.")



        if percent < 0 or percent > 100:

            raise ValueError(

                "Discount 0 se 100% ke beech hona chahiye."

            )



        return number - number * percent / 100



    match = re.fullmatch(

        r"(-?\d+(?:\.\d+)?)\s*(?:ka|ki|ke)\s*"

        r"(-?\d+(?:\.\d+)?)\s*%",

        question

    )



    if match:

        number = float(match.group(1))

        percent = float(match.group(2))

        return number * percent / 100



    match = re.fullmatch(

        r"(-?\d+(?:\.\d+)?)\s*%\s*"

        r"(?:of|ka|ki|ke)\s*"

        r"(-?\d+(?:\.\d+)?)",

        question

    )



    if match:

        percent = float(match.group(1))

        number = float(match.group(2))

        return number * percent / 100



    return None





def solve_ratio(question):

    question = question.strip().lower()

    question = question.replace("का", "ka")



    match = re.fullmatch(

        r"(\d+)\s*:\s*(\d+)\s*(?:simplify|simple|saral)?",

        question

    )



    if match:

        a = int(match.group(1))

        b = int(match.group(2))



        if a == 0 and b == 0:

            raise ValueError("0:0 ka ratio simplify nahi ho sakta.")



        divisor = math.gcd(a, b)

        return f"{a // divisor}:{b // divisor}"



    match = re.fullmatch(

        r"(\d+)\s*:\s*(\d+)\s*(?:ka\s*)?total\s+"

        r"(\d+(?:\.\d+)?)",

        question

    )



    if match:

        a = int(match.group(1))

        b = int(match.group(2))

        total = float(match.group(3))



        if a == 0 and b == 0:

            raise ValueError("Dono ratio parts zero nahi ho sakte.")



        if total < 0:

            raise ValueError("Total negative nahi ho sakta.")



        first = total * a / (a + b)

        second = total * b / (a + b)



        return (

            f"Pehla hissa = {format_answer(first)}, "

            f"Doosra hissa = {format_answer(second)}"

        )



    return None





def solve_profit_loss(question):

    question = question.strip().lower()



    match = re.fullmatch(

        r"(profit|loss)\s+percent\s+"

        r"(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)",

        question

    )



    if match:

        kind = match.group(1)

        cp = float(match.group(2))

        sp = float(match.group(3))



        if cp <= 0:

            raise ValueError("Cost price zero se zyada honi chahiye.")



        if sp < 0:

            raise ValueError("Selling price negative nahi ho sakti.")



        if kind == "profit":

            if sp <= cp:

                raise ValueError(

                    "Profit ke liye selling price, cost price se zyada honi chahiye."

                )

            return (sp - cp) / cp * 100



        if sp >= cp:

            raise ValueError(

                "Loss ke liye selling price, cost price se kam honi chahiye."

            )



        return (cp - sp) / cp * 100



    match = re.fullmatch(

        r"(profit|loss)\s+"

        r"(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)",

        question

    )



    if match:

        kind = match.group(1)

        cp = float(match.group(2))

        sp = float(match.group(3))



        if cp <= 0:

            raise ValueError("Cost price zero se zyada honi chahiye.")



        if sp < 0:

            raise ValueError("Selling price negative nahi ho sakti.")



        if kind == "profit":

            if sp <= cp:

                raise ValueError(

                    "Profit ke liye selling price, cost price se zyada honi chahiye."

                )

            return sp - cp



        if sp >= cp:

            raise ValueError(

                "Loss ke liye selling price, cost price se kam honi chahiye."

            )



        return cp - sp



    return None





def solve_interest(question):

    question = question.strip().lower()



    match = re.fullmatch(

        r"(si|ci)\s+(total\s+)?"

        r"(\d+(?:\.\d+)?)\s+"

        r"(\d+(?:\.\d+)?)\s+"

        r"(\d+(?:\.\d+)?)",

        question

    )



    if not match:

        return None



    kind = match.group(1)

    total_mode = match.group(2) is not None

    principal = float(match.group(3))

    rate = float(match.group(4))

    years = float(match.group(5))



    if not all(math.isfinite(x) for x in (principal, rate, years)):

        raise ValueError("Numbers valid hone chahiye.")



    if principal <= 0:

        raise ValueError("Principal zero se zyada hona chahiye.")



    if rate < 0 or rate > 1000:

        raise ValueError("Rate 0 se 1000% ke beech honi chahiye.")



    if years < 0 or years > 100:

        raise ValueError("Time 0 se 100 saal ke beech hona chahiye.")



    try:

        if kind == "si":

            interest = principal * rate * years / 100

            amount = principal + interest

        else:

            amount = principal * (1 + rate / 100) ** years

            interest = amount - principal

    except (OverflowError, ValueError):

        raise ValueError("Interest result bahut bada hai.")



    result = amount if total_mode else interest



    if not math.isfinite(result) or abs(result) > 10**100:

        raise ValueError("Interest result bahut bada hai.")



    return result





def solve_time_work(question):

    question = question.strip().lower()



    match = re.fullmatch(

        r"work\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)",

        question

    )



    if not match:

        return None



    first_days = float(match.group(1))

    second_days = float(match.group(2))



    if not math.isfinite(first_days) or not math.isfinite(second_days):

        raise ValueError("Days valid hone chahiye.")



    if first_days <= 0 or second_days <= 0:

        raise ValueError("Dono logon ke din zero se zyada hone chahiye.")



    combined_rate = (1 / first_days) + (1 / second_days)

    days = 1 / combined_rate



    if not math.isfinite(days):

        raise ValueError("Answer bahut bada hai.")



    return days





def solve_speed_distance_time(question):

    question = question.strip().lower()



    match = re.fullmatch(

        r"(speed|distance|time)\s+"

        r"(\d+(?:\.\d+)?)\s+"

        r"(\d+(?:\.\d+)?)",

        question

    )



    if not match:

        return None



    operation = match.group(1)

    first = float(match.group(2))

    second = float(match.group(3))



    if not math.isfinite(first) or not math.isfinite(second):

        raise ValueError("Numbers valid hone chahiye.")



    if first < 0 or second < 0:

        raise ValueError("Speed, distance aur time negative nahi ho sakte.")



    if operation == "speed":

        distance = first

        hours = second



        if hours == 0:

            raise ValueError("Time zero nahi ho sakta jab distance di ho.")



        result = distance / hours

        label = "Chaal"



    elif operation == "distance":

        speed = first

        hours = second

        result = speed * hours

        label = "Duri"



    else:

        distance = first

        speed = second



        if speed == 0:

            if distance == 0:

                raise ValueError(

                    "Zero distance aur zero speed par time nirdharit nahi hai."

                )

            raise ValueError("Speed zero hai, isliye distance tay nahi hogi.")



        result = distance / speed

        label = "Samay"



    if not math.isfinite(result) or abs(result) > 10**100:

        raise ValueError("Answer bahut bada hai.")



    return operation, result, label





def format_answer(answer):

    if isinstance(answer, float) and answer.is_integer():

        return int(answer)



    if isinstance(answer, float):

        return round(answer, 6)



    return answer





def print_age_difference(answer, hindi):

    first_age, second_age = answer



    if hindi:

        print("पहले व्यक्ति की उम्र:", format_answer(first_age), "साल")

        print("दूसरे व्यक्ति की उम्र:", format_answer(second_age), "साल")

    else:

        print("Pehle vyakti ki umar:", format_answer(first_age), "saal")

        print("Doosre vyakti ki umar:", format_answer(second_age), "saal")





def print_father_son(answer, hindi):

    father_age, son_age = answer



    if hindi:

        print("बेटे की वर्तमान उम्र:", format_answer(son_age), "साल")

        print("पिता की वर्तमान उम्र:", format_answer(father_age), "साल")

    else:

        print("Bete ki vartaman umar:", format_answer(son_age), "saal")

        print("Pita ki vartaman umar:", format_answer(father_age), "saal")





def solve_math():

    print("\n=== SSC CHSL Offline Solver ===")

    print("Calculator: 25 + 4")

    print("Percentage: 500 ka 20%")

    print("Increase: 500 me 20% badhao")

    print("Discount: 800 par 15% chhoot")

    print("Ratio: 10:20 simplify")

    print("Age ratio: age 5 3 40")

    print("Age difference: age difference 12 ratio 5 3")

    print("Father-son: father son 4 future 5 3")

    print("Average: average 10 20 30")

    print("HCF: hcf 12 18")

    print("LCM: lcm 12 18")

    print("Profit: profit 120 150")

    print("Loss: loss 150 120")

    print("Simple interest: si 1000 5 2")

    print("Compound interest: ci 1000 10 2")

    print("Time and work: work 10 5")

    print("Speed: speed 120 2")

    print("Distance: distance 60 3")

    print("Time: time 120 60")

    print("Hindi questions bhi pooch sakte hain.")

    print("Band karne ke liye exit likhein.")



    while True:

        original_question = input("\nSawal: ").strip()



        if original_question.lower() == "exit":

            print("Solver band ho gaya.")

            break



        if not original_question:

            print("Pehle sawal likhein.")

            continue



        if len(original_question) > 250:

            print("Sawal bahut lamba hai.")

            continue



        hindi = is_hindi(original_question)

        question = normalize_question(original_question)



        try:

            answer = solve_age_difference(question)



            if answer is not None:

                print_age_difference(answer, hindi)

                continue



            answer = solve_father_son_age(question)



            if answer is not None:

                print_father_son(answer, hindi)

                continue



            answer = solve_age(question)



            if answer is not None:

                print_age_difference(answer, hindi)

                continue



            answer = solve_hcf_lcm(question)



            if answer is not None:

                if hindi:

                    print("उत्तर:", answer)

                else:

                    print("Jawab:", answer)

                continue



            answer = solve_average(question)



            if answer is not None:

                if hindi:

                    print("औसत:", format_answer(answer))

                else:

                    print("Average:", format_answer(answer))

                continue



            answer = solve_profit_loss(question)



            if answer is not None:

                if "percent" in question:

                    if hindi:

                        print("उत्तर:", format_answer(answer), "%")

                    else:

                        print("Jawab:", format_answer(answer), "%")

                elif question.startswith("profit"):

                    print("Profit:", format_answer(answer))

                else:

                    print("Loss:", format_answer(answer))

                continue



            answer = solve_interest(question)



            if answer is not None:

                if question.startswith("si"):

                    label = (

                        "कुल राशि" if hindi and "total" in question

                        else "साधारण ब्याज" if hindi

                        else "Kul rashi" if "total" in question

                        else "Simple interest"

                    )

                else:

                    label = (

                        "कुल राशि" if hindi and "total" in question

                        else "चक्रवृद्धि ब्याज" if hindi

                        else "Kul rashi" if "total" in question

                        else "Compound interest"

                    )



                print(label + ":", format_answer(answer))

                continue



            answer = solve_time_work(question)



            if answer is not None:

                if hindi:

                    print(

                        "दोनों मिलकर काम पूरा करेंगे:",

                        format_answer(answer),

                        "दिन"

                    )

                else:

                    print(

                        "Dono milkar kaam poora karenge:",

                        format_answer(answer),

                        "din"

                    )

                continue



            answer = solve_speed_distance_time(question)



            if answer is not None:

                operation, result, label = answer

                result = format_answer(result)



                if hindi:

                    hindi_labels = {

                        "speed": "चाल",

                        "distance": "दूरी",

                        "time": "समय",

                    }

                    print(hindi_labels[operation] + ":", result)

                elif operation == "speed":

                    print(label + ":", result, "km/h")

                elif operation == "distance":

                    print(label + ":", result, "km")

                else:

                    print(label + ":", result, "ghante")



                continue



            answer = solve_percentage(question)



            if answer is not None:

                if hindi:

                    print("उत्तर:", format_answer(answer))

                else:

                    print("Jawab:", format_answer(answer))

                continue



            answer = solve_ratio(question)



            if answer is not None:

                if hindi:

                    print("उत्तर:", answer)

                else:

                    print("Jawab:", answer)

                continue



            answer = solve_knowledge(original_question)

            if answer is not None:
                print(answer)
                continue

            answer = solve_reasoning(question)

            if answer is not None:
                print(answer)
                continue

            # Safe normal calculator. eval() ka use nahi hota.

            question = question.replace("^", "**")



            if not re.fullmatch(r"[0-9+\-*/().\s]+", question):

                if hindi:

                    print("यह सवाल अभी समर्थित नहीं है।")

                else:

                    print("Sawal ka format supported nahi hai.")

                continue



            tree = ast.parse(question, mode="eval")

            answer = calculate(tree.body)



            if hindi:

                print("उत्तर:", format_answer(answer))

            else:

                print("Jawab:", format_answer(answer))



        except (

            ValueError,

            SyntaxError,

            ZeroDivisionError,

            OverflowError

        ) as error:

            if hindi:

                print("सवाल हल नहीं हुआ:", error)

            else:

                print("Sawal hal nahi hua:", error)





if __name__ == "__main__":

    solve_math()