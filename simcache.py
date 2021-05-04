'''Simulador de cache:
Aceita configuração de sistemas com apenas L1 e de sistemas com L1 e L2.'''

# Bibliotecas
import sys

# Constantes
N_BYTES_PALAVRA = int(4)

# Estruturas
def pos_cache(bit_validade, tag, ordem_acesso):
	return {'bit_validade': int(bit_validade), 'tag': int(tag), 'ordem_acesso': int(ordem_acesso)}

# Codigo cache.c traduzido para Orientacao a Objetos
class Cache:
	def __init__(self, n_blocos = 1, associatividade = 1, n_palavras_bloco = 1) -> None:
		'''Versão python para := void aloca_cache(t_cache *cache, int n_blocos, int associatividade, int n_palavras_bloco)
		Aloca e inicializa a cache.'''

		# Inicializa parametros da configuracao
		self.n_blocos         = int(n_blocos)                             # Numero total de blocos da cache
		self.associatividade  = int(associatividade)                      # Numero de blocos por conjunto
		self.n_palavras_bloco = int(n_palavras_bloco)                     # Numero de palavras do bloco
		self.n_conjuntos      = int(self.n_blocos / self.associatividade) # Numero de conjuntos da cache
		self.conjunto         = []
		self.new_cache()

	def new_cache(self):
		'''Cria e inicializa a cache.'''
		for i in range(self.n_conjuntos):
			self.conjunto.append( [] )
			for j in range(self.associatividade):
				self.conjunto[i].append( pos_cache(0,0,0) )

	def busca_e_insere_na_cache(self, endereco=0) -> int:
		'''Versão python para := int busca_e_insere_na_cache(t_cache *cache, int endereco)
		Busca dado na cache e, se não encontra, insere-o.
		Valor de retorno: 0 (acerto) ou 1 (falha).'''
		
		endereco_palavra = int(endereco / N_BYTES_PALAVRA)
		endereco_bloco   = int(endereco_palavra / self.n_palavras_bloco)
		indice           = int(endereco_bloco % self.n_conjuntos)
		tag              = int(endereco_bloco / self.n_conjuntos)
		i_acerto         = -1          # Posicao que causou acerto
		i_livre          = -1          # Primeira posicao livre encontrada no conjunto
		i_lru            = -1          # Posição com menor valor de ordem_acesso no conjunto (bloco LRU)
		ordem_min        = sys.maxsize # Dentre as posicoes ocupadas no conjunto, menor valor de ordem_acesso
		ordem_max        = -1          # Dentre as posicoes ocupadas no conjunto, maior valor de ordem_acesso
		result           = 0

		# Procura dado na cache
		for i in range(self.associatividade):
			if self.conjunto[indice][i]['bit_validade'] == 1:
				# Posicao possui dado valido
				if self.conjunto[indice][i]['tag'] == tag:
					# Acerto
					i_acerto = i
				if ordem_max < self.conjunto[indice][i]['ordem_acesso']:
					ordem_max = self.conjunto[indice][i]['ordem_acesso']
				if ordem_min > self.conjunto[indice][i]['ordem_acesso']:
					i_lru     = i
					ordem_min = self.conjunto[indice][i]['ordem_acesso']
			else:
				# Posicao nao possui dado valido
				if i_livre == -1:
					i_livre = i
		
		if i_acerto!= -1:
			# Acerto
			self.conjunto[indice][i_acerto]['ordem_acesso'] = ordem_max + 1
		elif i_livre != -1:
			# Falha SEM substitucao
			self.conjunto[indice][i_livre]['bit_validade'] = 1
			self.conjunto[indice][i_livre]['tag']          = tag
			self.conjunto[indice][i_livre]['ordem_acesso'] = ordem_max + 1
			result = 1
		else:
			# Falha COM substitucao
			if i_lru == -1:
				i_lru = 0 # nao fez diferenca no resultado alterar de -1 para 0
			self.conjunto[indice][i_lru]['tag']          = tag
			self.conjunto[indice][i_lru]['ordem_acesso'] = ordem_max + 1
			result = 1

		return result

# Programa principal
if __name__ == "__main__":
	try:
		nome_arq_config    = sys.argv[1]
		nome_arq_acessos   = sys.argv[2] # Arquivo possui um "inteiro" por linha 
		result_acesso      = 0
		endereco           = 1	         # Endereco de memoria acessado
		L2_f               = False

		# Abre arquivo de configuracao e le n_blocos, associatividade e n_palavras_bloco da cache L1
		try:
			f = open(nome_arq_config, 'r')
			arq_config = f.readlines()
			f.close()

			# L1 apenas
			n_blocosL1         = int(arq_config[0])  # Numero total de blocos da cache L1
			associatividadeL1  = int(arq_config[1])  # Numero de blocos por conjunto da cache L1
			n_palavras_blocoL1 = int(arq_config[2])  # Numero de palavras do bloco da cache L1
			
			# Verifica se existe cache L2
			conf_count = 0
			for j in arq_config:
				if j != '':
					conf_count += 1
			if conf_count > 5:
				L2_f = True
			
			if L2_f:
				n_blocosL2         = int(arq_config[3])  # Numero total de blocos da cache L2
				associatividadeL2  = int(arq_config[4])  # Numero de blocos por conjunto da cache L2
				n_palavras_blocoL2 = int(arq_config[5])  # Numero de palavras do bloco da cache L2

			# Abre arquivo de acessos
			try:
				f = open(nome_arq_acessos, 'r')
				arq_acessos = f.readlines()
				f.close()

				# Inicializa medidas de desempenho
				n_acessos_cacheL1 = 0 # Numero total de acessos a cache L1
				n_falhas_cacheL1  = 0 # Numero de falhas na cache L1
				n_falhas_cacheL2  = 0 # Numero de falhas na cache L2

				# Aloca e inicializa estrutura de dados da cache L1
				L1 = Cache(n_blocos=n_blocosL1, associatividade=associatividadeL1, n_palavras_bloco=n_palavras_blocoL1)
				if L2_f:
					L2 = Cache(n_blocos=n_blocosL2, associatividade=associatividadeL2, n_palavras_bloco=n_palavras_blocoL2)

				#  Leitura dos enderecos do arquivo de acessos
				for i in arq_acessos:
					if i != '':
						# Possivelmente tem linhas em branco no arquivo
						# Como usei readlines() para colocar o arquivo numa lista de strings, nao preciso me preocupar com EOF
						endereco           = int(i)
						result_acesso      = L1.busca_e_insere_na_cache(endereco=endereco)
						n_acessos_cacheL1 += 1
						if result_acesso == 1:
							n_falhas_cacheL1 += 1
							if L2_f:
								n_acessos_cacheL2 = n_falhas_cacheL1
								result_acessoL2   = L2.busca_e_insere_na_cache(endereco=endereco)
								if result_acessoL2 == 1:
									 n_falhas_cacheL2 += 1
				# Finalizacao

				# Imprime medidas de desempenho
				if L2_f:
					print("%10d %10d %10d %10d"%(n_acessos_cacheL1, n_falhas_cacheL1, n_acessos_cacheL2, n_falhas_cacheL2))
				else:
					print("%10d %10d"%(n_acessos_cacheL1, n_falhas_cacheL1))
			except FileNotFoundError:
				print("\nArquivo de acessos não encontrado\n")
		except FileNotFoundError:
			print("\nArquivo de configuração não encontrado\n")
	except IndexError:
		print("\nUso: python3 simcache.py arquivo_configuracao arquivo_acessos\n")
