"""AED reprodutível: dados institucionais do TikTok e microdados públicos (se fornecidos).
Uso: python analise_exploratoria_tiktok_shop_revisada.py --arquivo dados/arquivo.xlsx
Dependências: pandas matplotlib openpyxl (para xlsx).
"""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

OUT = Path('resultados')
OUT.mkdir(exist_ok=True)

# Fonte: TikTok Newsroom, 04/06/2026. Múltiplos de crescimento não são volumes absolutos.
indicadores = pd.DataFrame({'indicador':['GMV médio diário mensal','Criadores afiliados ativos','Lives diárias','GMV de lives'], 'multiplicador':[102,46,20,161]})
indicadores.to_csv(OUT/'indicadores_institucionais.csv', index=False)
fig, ax = plt.subplots(figsize=(9,4))
b = ax.barh(indicadores['indicador'], indicadores['multiplicador'], color=['#18cbd0','#ed3979','#18cbd0','#ed3979'])
ax.invert_yaxis(); ax.bar_label(b,labels=[f'{v}×' for v in indicadores['multiplicador']],padding=3)
ax.set_xlabel('Multiplicador divulgado (vezes)');fig.tight_layout();fig.savefig(OUT/'crescimento.png',dpi=180);plt.close(fig)
fig, ax = plt.subplots(figsize=(6,5))
ax.pie([57.8,42.2],labels=['Compraram após descoberta','Complemento percentual'],autopct='%1.1f%%',startangle=90,colors=['#ed3979','#18cbd0'])
fig.tight_layout();fig.savefig(OUT/'compra_apos_descoberta.png',dpi=180);plt.close(fig)

parser=argparse.ArgumentParser(description='Explorar dados abertos de compra impulsiva no TikTok Shop')
parser.add_argument('--arquivo',help='Caminho do CSV/XLSX baixado da fonte acadêmica; opcional')
args=parser.parse_args()
if args.arquivo:
    path=Path(args.arquivo)
    if not path.is_file(): raise FileNotFoundError(f'Arquivo não encontrado: {path}')
    if path.suffix.lower() in ('.xlsx','.xls'):
        df=pd.read_excel(path)
    elif path.suffix.lower()=='.csv':
        try: df=pd.read_csv(path)
        except UnicodeDecodeError: df=pd.read_csv(path,encoding='latin1')
    else: raise ValueError('Use CSV ou XLSX')
    print('Dimensão:',df.shape,'\nColunas:',df.columns.tolist())
    pd.DataFrame({'tipo':df.dtypes.astype(str),'ausentes':df.isna().sum(),'percentual_ausente':df.isna().mean()*100}).to_csv(OUT/'qualidade.csv')
    df.describe(include='all').transpose().to_csv(OUT/'estatisticas.csv')
    print('Linhas duplicadas:',df.duplicated().sum())
    numericas=df.select_dtypes(include='number')
    if not numericas.empty:
        numericas.hist(figsize=(12,8),bins=15)
        plt.tight_layout();plt.savefig(OUT/'distribuicoes_numericas.png',dpi=160);plt.close('all')
        if numericas.shape[1]>1:
            corr=numericas.corr(numeric_only=True)
            corr.to_csv(OUT/'correlacoes.csv')
            fig,ax=plt.subplots(figsize=(max(6,len(corr)*.7),max(5,len(corr)*.7)))
            im=ax.imshow(corr,vmin=-1,vmax=1,cmap='coolwarm')
            ax.set_xticks(range(len(corr)),corr.columns,rotation=90);ax.set_yticks(range(len(corr)),corr.index)
            fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(OUT/'correlacoes.png',dpi=160);plt.close(fig)
    for col in df.select_dtypes(exclude='number').columns[:8]:
        safe=''.join(c if c.isalnum() or c in '-_' else '_' for c in str(col))
        df[col].value_counts(dropna=False).head(15).to_csv(OUT/f'frequencias_{safe}.csv')
    print('Relatórios criados em',OUT.resolve())
else:
    print('Gráficos institucionais criados. Para AED dos 361 registros, baixe a base Mendeley e informe --arquivo.')
