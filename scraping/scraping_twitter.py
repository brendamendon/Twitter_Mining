from bs4 import BeautifulSoup
from csv import DictWriter
import pickle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time

class Cookies:

    def aplica_cookies(driver, dir):

        try:
            # Carrega os cookies
            cookies = pickle.load(open(fr'{dir}\cookies.pkl', "rb"))

            # Deleta os cookies da página
            driver.delete_all_cookies()

            for cookie in cookies:
                # Verifica a chave 'expiry' do cookie (que é um dicionário)
                if isinstance(cookie.get('expiry'), float):
                    cookie['expiry'] = int(cookie['expiry']) 

                # Aplica o valor da chave no driver da página
                driver.add_cookie(cookie)
            print("Os cookies foram aplicados com sucesso!")

        except:
            print("Houve um problema ao aplicar os cookies")
            raise Exception
        
        return driver


class Acesso:

    def init_driver(driver_type, page, dir):

        try:
        # Define qual driver será utilizado
            if driver_type == 1:
                driver = webdriver.Firefox()

            elif driver_type == 2:
                driver = webdriver.Chrome()

            elif driver_type == 3:
                driver = webdriver.Ie()
                
            elif driver_type == 4:
                driver = webdriver.Opera()

            elif driver_type == 5:
                driver = webdriver.PhantomJS()
        
            # Aguardando 5 segundos para continuar a execução do código
            driver.wait = WebDriverWait(driver, 5)

            # Abre a página
            driver.get(page)

        except Exception as e:
                print("Não foi possível inciar o driver!, vide erro: {}".format(e))

        time.sleep(3)
        driver = Cookies.aplica_cookies(driver, dir)

        return driver


class Output:

    def write_csv(nome, user, tweet_date, tweet_text):

        try:
            # Abre um arquivo em modo escrita e leitura            
            with open(r"bases\tweets.csv", "a+", encoding='utf-8') as csv_file:
                # Definindo os nomes dos campos para cada coluna
                fieldnames = ['Nome', 'Username', 'Data', 'Texto']

                # Cria um dicionário com as linhas do csv
                writer = DictWriter(csv_file, fieldnames=fieldnames)

                # Grava os dados no arquivo csv
                writer.writerow({'Nome': nome, 'Username': user, 'Data': tweet_date, 'Texto': tweet_text})

        except Exception as e:
            print("Não foi possível criar o csv!, vide erro:\n\n {}".format(e))


class Scrapping:

    def montagem_html(word, lang, start_date, end_date):

        # Idiomas para filtrar os tweets
        languages = { 1: 'en', 2: 'pt', 3: 'es', 4: 'fr', 5: 'de', 6: 'ru', 7: 'zh'}

        # Construção da URL para busca avançada
        url = "https://twitter.com/search?lang=pt&q="
        url += "%24{0}%20(%24{0})".format(word)
        url += "%20lang%3A{}".format(languages[lang])
        url += "%20until%3A{0}%20since%3A{1}".format(end_date, start_date)
        url += "%20-filter%3Areplies&src=typed_query"
        print('URL de busca:\n\n',url)

        return url

    def scrapping_selenium(driver, url, max_time):

        driver.get(url)

        # Armazena a posição da página antes de rolar
        previous_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(8)

            # Armazena a posição da página após a rolagem
            current_height = driver.execute_script("return document.body.scrollHeight")

            # Se as duas posições forem iguais, o loop é interrompido, indicando que a página chegou ao final
            if current_height == previous_height:
                break
            
            previous_height = current_height

            try:
                # Pegando o código html dos tweets
                tweet_divs = driver.page_source
                soup = BeautifulSoup(tweet_divs, "html.parser")
                content = soup.find_all('article')

                for c in content:
                    try:
                        # Capturando o texto do tweet
                        tweet_text = c.find('div', {'data-testid': 'tweetText'}).text
                        tweet_text = tweet_text.replace('\n', ' ').replace('\r', ' ')

                        # Capturando o nome e usuário da pessoa que fez o tweet
                        tweet_name = c.find('div', {'data-testid': 'User-Name'}).text.strip()
                        name_parts = tweet_name.split('@')
                        nome = name_parts[0]
                        nome = nome.replace(',', '')
                        user = '@' + name_parts[1].split('·')[0]

                        # Capturando a data do tweet
                        date_elem = c.find('time')
                        tweet_date = date_elem.text.strip()

                        print(f"Nome: {nome}")
                        print(f"User: {user}")
                        print(f"Data: {tweet_date}")
                        print(f"Tweet: {tweet_text}")
                        print("----------------------")

                        try:
                            Output.write_csv(nome, user, tweet_date, tweet_text)
                        except:
                            print('csv error')

                    except:
                        pass

            except Exception as e:
                print("Não foi possível fazer o scraping!, vide erro:\n\n {}".format(e))
                driver.quit()


''' 
    CÓDIGO PRINCIPAL 
'''

# Chave que define o navegador
driver_type = 2

# Lista de strings a serem buscadas nos tweets
word = 'TSLA'

# Diretório do arquivo .pkl com os cookies de autenticação de login
diretorio = r'pkl'

# Pagina inicial para autenticação
page = "https://twitter.com/home"

# Define o range de datas para a pesquisa
start_date = '2023-05-02'
end_date = '2023-05-03'

# Chave que define o idioma dos tweets
lang = 1

# Tempo de busca dos tweets em segundos
max_time = 600

# Montagem Url
url = Scrapping.montagem_html(word, lang, start_date, end_date)

# Cria o Driver
driver = Acesso.init_driver(driver_type, page, diretorio)

# Inicia o Scrapping
print("Iniciando o processo de scraping...")
start_time = time.time()
Scrapping.scrapping_selenium(driver, url, max_time)
end_time = time.time()
elapsed_time = end_time - start_time
print("Processo de scraping concluído!")
print("Tempo total decorrido: {:.2f} segundos".format(elapsed_time))

# Fecha o navegador e encerra sua instância
driver.quit()
