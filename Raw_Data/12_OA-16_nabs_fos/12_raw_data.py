from tqdm import tqdm

import json
import pandas as pd


FNAME_PROCESSED_KEY_TERMS = "12_ProcessedKeyTerms.json"


replacables_symbols = ["&" , "-"  , '"' ,  "  "]
replacables_words = ["and" , "or" , "for", "&" , "of" , "sdg" , "oecd" , "arctic"]

def pre_proc(list_o_strings):
    processed = []
    alpha = "abcdefghijklmnopqrstuvwxyz0123456789 "
    for item in list_o_strings :
        item = item.replace("_" , " ")
        item = item.lower()

        for c in replacables_symbols:
            item = item.replace(c, " ")
        item_p = item.split()
        item = " ".join(i for i in item_p if i not in replacables_words)

        if all(c in alpha for c in item) :
            if item.startswith(" ") :
                item = item[1:]
            if item.endswith(" ") :
                item = item[:-1]
            if len(item) > 4:
                if item not in processed:
                    processed.append(item)
    return processed


if __name__ == '__main__':
    fos_data = pd.read_excel('NABS_FOS_update_2020-08-20_ed_VS.xlsx')[['FOS NAME', 'FOS NUMBER', 'SDG']].drop_duplicates()

    # Blacklist
    blacklist = set()
    for fos_name, fos_id, sdg_nr in fos_data.values:
        if sdg_nr == 'NOT RELEVANT':
            blacklist.add((fos_id, fos_name))

    pd.DataFrame(blacklist, columns=['fos_id', 'fos_name']).to_csv('12_Blacklist.csv', index=False)

    # 
    sdg_fos = dict()
    for fos_name, fos_id, sdg_nr in tqdm(fos_data[~fos_data['FOS NUMBER'].isin(list(map(lambda v: v[0], blacklist)))].values):
        sdg_label = f'SDG_{sdg_nr}'
        if sdg_label not in sdg_fos.keys():
            sdg_fos[sdg_label] = []
        sdg_fos[sdg_label].append(fos_name)

    for sdg_label, foses in sdg_fos.items():
        sdg_fos[sdg_label] = pre_proc(foses)

    print('-' * 100)
    counter = 0
    with open('update_info.txt', 'w') as file_:
        print('SDG\tCount\n')
        file_.write('SDG\tCount')
        for sdg_label in sorted(sdg_fos.keys(), key=lambda x: int(x.split('_')[1])):
            foses = sdg_fos[sdg_label]
            print(f'{sdg_label}\t{len(foses)}')
            file_.write(f'{sdg_label}\t{len(foses)}\n')
            counter += len(foses)
        print(f'\nOverall : {counter}')
        file_.write(f'Overall : {counter}')

    with open(FNAME_PROCESSED_KEY_TERMS, 'w') as file_:
        json.dump(sdg_fos, file_)
