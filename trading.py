from datetime import datetime
from os import listdir, remove
from os.path import isfile, join

import fire
from utils import revert_dict

class MOEX_contract:
    code_short2long = {'GD':'GOLD',
        'BR':'BR',
        'SI':'SI',
        'RI':'RTS',
        'GZ':'GAZR',
        'SR':'SBRF'}
    
    letter2month = {
            'H':'3',
            'M':'6',
            'U':'9',
            'Z':'12'
        }

    def __init__(self, short_name=None, long_name=None):
        """
            example of short code: SIM9
            example of long code: Si-6.19
        """
        
        if short_name is None and long_name is None:
            raise ValueError('You have provide short or long code')
        
        if not (short_name is None or long_name is None):
            raise ValueError('You have provide only one code')
        
        if short_name:
            if len(short_name) != 4: raise ValueError('short code shall have 4 chars')
            self.code = short_name[:2].upper()
            self.month = short_name[2].upper()
            self.year =  short_name[3].upper()

        if long_name:
            long_code = long_name.split('-')[0].upper()
            dt = long_name.split('-')[1]
            month = dt.split('.')[0]
            year = dt.split('.')[1]
            self.code = self._long2short(long_code)
            self.month = self._month2letter(month)
            self.year = self._year_long2short(year)

    @classmethod
    def _letter2month(cls, letter):
        return cls.letter2month[letter]

    @classmethod
    def _month2letter(cls, month):
        return revert_dict(cls.letter2month)[month]

    @classmethod
    def _short2long(cls, short):
        return cls.code_short2long[short]

    @classmethod
    def _long2short(cls, long):
        return revert_dict(cls.code_short2long)[long]

    @classmethod
    def _year_short2long(cls, short):
        year = int(short)
        if year == 0: return '20'
        return '1' + short

    @classmethod
    def _year_long2short(cls, long):
        return long[-1]

    @property
    def short_name(self):
        return self.code + self.month + self.year

    @property
    def long_month(self):
        return self._letter2month(self.month) 
    
    @property
    def long_code(self):
        return self._short2long(self.code)
    
    @property
    def long_year(self):
        return self._year_short2long(self.year)

    @property
    def long_name(self):
        return f'{self.long_code}-{self.long_month}.{self.long_year}'

    @property
    def is_main_from(self):
        if self.long_month == '3': month = 1
        if self.long_month == '6': month = 3
        if self.long_month == '9': month = 6
        if self.long_month == '12': month = 9
        return datetime(int('20'+self.long_year), month, 15)
    
    @property
    def is_main_to(self):
        return datetime(int('20'+self.long_year), int(self.long_month), 15)

class Orchestrator:
    def drop_not_main_futures_from_folder(self, folder:str):
        file_names = [f for f in listdir(folder) if isfile(join(folder, f))]
        # sample filename Si-3.17.2017-02-09.OrdLog.qsh
        
        for fname in file_names:
            long_name = fname[:-22]
            contract = MOEX_contract(long_name=long_name)

            dt = fname[-21:-11]
            dt_obj = datetime.strptime(dt, '%Y-%m-%d')
            if dt_obj < contract.is_main_from:
                remove(join(folder, fname))
                print(f'Removed {folder}{fname}')


if __name__ == "__main__":
    fire.Fire(Orchestrator)
