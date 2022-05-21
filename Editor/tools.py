import math

def NumToBytecount(num):
    if num < 1000:
        return f"{num} B"

    if num < 1000000:
        return f"{math.floor(num/10)/100} KB"
        
    if num < 1000000000:
        return f"{math.floor(num/10000)/100} MB"