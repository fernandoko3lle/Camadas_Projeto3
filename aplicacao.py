#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM7"                  # Windows(variacao de)


def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        
        # Espera um byte de sacrificio
        print("esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)
        print('recebeu o byte de sacrificio')

        # Imagem a ser salva
        imageW = "Camadas_Projeto3\img\imagem.png"

        # Função de bytes para inteiros
        def bytes_to_int(bytes):
            return int.from_bytes(bytes, 'big')
        
        # Função de inteiros para bytes 
        def int_to_byte(num):
            return int(num).to_bytes(1, 'big')

        # Finaliza a comunicação
        def finaliza_comunicacao():
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")
            com1.disable()

        # Definindo Head como fazio
        head = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        eop = b'\xAA\xBB\xCC\xDD'
        payload = bytearray()
        num_servidor = b'\xee'
        total_pacotes = 0

        # Recebendo primeiro comando
        txBuffer, nRx = com1.getData(10) 

        head = list(head)
        head[0] = txBuffer[0]
        head[1] = txBuffer[1]
        head[2] = txBuffer[2]
        head = bytearray(head)
        print('-----')
        eop_recebido,_ = com1.getData(4)
        print(f"eop recebido: {eop_recebido}\n ")

        if head[0] == 1:
            if int_to_byte(head[1]) == num_servidor:
                print('número do servidor verificado\n ')
                if  eop_recebido == eop:
                    print("Eop verificado\n ")
                    total_pacotes = head[2]
                    print('Mensagem recebida com sucesso')
                    head = list(head)
                    head[0] = 2
                    head = bytearray(head)
                    datagrama = head + payload + eop
                    # print(f'datagrama_1: {datagrama}')
                    com1.sendData(datagrama)
                    print('msg enviada para o client\n')

                else:
                    print('!--------------!')
                    print('eop não coincide')   
                    print(f'eop recebido: {eop_recebido}; eop: {eop}')
                    print('!--------------!')
            else:
                print("Mensagem enviada para o servidor errado")
        else:
            print("Erro ao receber a mensagem")
        
        start_time_geral = time.time()
        array_img = bytearray()
        print(f'total_pacotes: {total_pacotes}')
        for i in range(total_pacotes):
            start_time = time.time()
            curent_time = time.time()
            enlapsed_time = curent_time - start_time
            time.sleep(1)
            while (len(com1.rx.buffer) < 10 and (time.time() - start_time) < 10):
                curent_time = time.time()
                enlapsed_time = curent_time - start_time
                if enlapsed_time > 2:
                    head = list(head)
                    head[0] = 4
                    head = bytearray(head)
                    payload = bytearray()
                    diagrama = head + payload + eop
                    com1.sendData(diagrama)
                    print('Contato perdido, enviando requisição...')
                    time.sleep(1)
            if enlapsed_time >= 10:
                print(head)
                head[0] = 5
                payload = bytearray()
                diagrama = head + payload + eop
                com1.sendData(diagrama)
                print('Tempo de resposta expirado')
                finaliza_comunicacao()
                break

            while com1.rx.buffer[1] != (i+1):
                head = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                payload = bytearray()
                head = list(head)
                head[0] = 6
                head[6] = i+1
                head = bytearray(head)
                diagrama = head + payload + eop
                com1.sendData(diagrama)
                time.sleep(.1)
                print(f'rxbuffer_1: {int_to_byte(com1.rx.buffer[1])}')
                print(f'rxbuffer: {com1.rx.buffer}')
                print(f'diagrama:{diagrama}')
                print('Numero do pacote não corresponde')
                print(f'i: {i}')
            if (i+1) == com1.rx.buffer[1]: 
                head,_ = com1.getData(10)
                tamanho_pacote = head[2]
                if head[0] == 3:
                    payload,_ = com1.getData(tamanho_pacote) 
                    array_img += payload
                    eop_recebido,_ = com1.getData(4)
                    if eop_recebido == eop:
                        head = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        head = list(head)
                        head[0] = 4
                        head[1] = i+1
                        head = bytearray(head)
                        payload = bytearray()
                        diagrama = head + payload + eop
                        com1.sendData(diagrama)
                        print(f'Pacote {i+1} lido')
                        time.sleep(.1)
                    else:
                        head = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        payload = bytearray()
                        head = list(head)
                        head[0] = 6
                        head[6] = i+1
                        head = bytearray(head)
                        diagrama = head + payload + eop
                        com1.sendData(diagrama)
                        print("Dado corrompido")
            else:
                print('.')
        curent_time = time.time()
        enlapsed_time = curent_time - start_time_geral
        print(enlapsed_time)
        print(f'array da img: {array_img}')
        f = open(imageW, 'wb')
        f.write(array_img)
        f.close




        # txBuffer = open(imageR, 'rb').read()  #isso é um array de bytes
       
        # print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))

        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
       
            
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmita arrays de bytes!
               
        
        # com1.sendData(np.asarray(txBuffer))  #as array apenas como boa pratica para casos de ter uma outra forma de dados
          
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        
        
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
          
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
