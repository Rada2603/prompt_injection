import re

import pandas as pd
import spacy
from autocorrect import Speller
from fuzzywuzzy import process

nlp = spacy.load("en_core_web_sm")
df = pd.read_csv("/home/stefan/Documents/rada/data.csv")
stock = pd.read_csv("/home/stefan/Downloads/stocks.csv")
stock_names_df = df["Stock Name"].unique()
stock_names= stock["name"]
stock_symbol = stock["symbol"].unique()
spell = Speller()

def extract_company_tokens(sentence):
    doc = nlp(sentence)
    company_tokens = [token.text.lower() for token in doc if token.ent_type_ == 'ORG']
    if  not company_tokens:
        corected_sentence =spell(sentence)
        doc = nlp(corected_sentence)
        company_tokens = [token.text.lower() for token in doc if token.ent_type_ == 'ORG']
    return company_tokens

def assign_stock_name(sentence, stock_symbol):
    extracted_company_tokens = extract_company_tokens(sentence)
    if extracted_company_tokens:
        best_match = process.extractOne(extracted_company_tokens[0], stock_names)[0]
        index = stock_names[stock_names == best_match].index[0]
        
        return stock_symbol[index].lower()
  
    else:
        words = [token.text.lower() for token in nlp(sentence)if token.is_alpha]
        stock_symbol_lower = [str(name).lower() for name in stock_symbol]
        for word in words:
            best_match ,score= process.extractOne(word,stock_symbol_lower)
            if score== 100:  
                return best_match
            else:
                continue
        for word in words:
            stock_symbol_matched = None 
            stock_names_lower = [str(name).lower() for name in stock_names]
            best_match,score = process.extractOne(word, stock_names_lower)
            if score==79 :
                matching_index = stock_names_lower.index(best_match)
                stock_symbol_matched = stock_symbol[matching_index]
                
        if stock_symbol_matched is not None:
            return stock_symbol_matched.lower()
        else:
            return str(None)
incorrect_count = 0

for index, row in df.iterrows():
   
    assigned_stock_name = assign_stock_name(row['User Prompt'], stock_symbol)
    real_stock_name = row['Stock Name']
    if assigned_stock_name.lower()!= real_stock_name.lower():
        
        incorrect_count += 1

print("Ukupno pogrešno dodeljenih akcija:", incorrect_count)
print("Procenat tačnosti:", (1 - incorrect_count / len(df)) * 100, "%")