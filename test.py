import requests

url = "https://github.com/Aloyss59/app"

resposne = requests.get(url)
print(f"réponse du site : {resposne}\n Site : {url}")

print("<3")