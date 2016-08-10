# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 13:54:31 2016

@author: Souzan
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 14:40:17 2016

@author: Souzan
"""

def readfromserial(ser):
    while True:
            x=ser.read()
            num=[]
            if x=='e':
                while x!='n':
                    x=ser.read()
                    if (x=='0' or x=='1' or x=='2' or x=='3' or x=='4' or x=='5' or x=='6' or x=='7' or x=='8' or x=='9'):         
                        num.append(int(x))            
                if x=='n':
                    val=0
                    for j in range(0,len(num)):
                        val+=float(num[j]*10**(len(num)-j-3))#works when reading in ADC value       
                    if val>3.3: 
                        return '0'
                    else:
                        return ['e',val]
            if x=='g':
                while x!='n':
                    x=ser.read()
                    if (x=='0' or x=='1' or x=='2' or x=='3' or x=='4' or x=='5' or x=='6' or x=='7' or x=='8' or x=='9'):         
                        num.append(int(x))            
                if x=='n':
                    val=0
                    for j in range(0,len(num)):
                        val+=float(num[j]*10**(len(num)-j-3))#works when reading in ADC value       
                    if val>3.3: 
                        return '0'
                    else:
                        return ['g',val]
            if x=='t':
                while x!='n':
                    x=ser.read()
                    if (x=='0' or x=='1' or x=='2' or x=='3' or x=='4' or x=='5' or x=='6' or x=='7' or x=='8' or x=='9'):         
                        num.append(int(x))            
                if x=='n':
                    val=0
                    for j in range(0,len(num)):
                        val+=float(num[j]*10**(len(num)-j-3))#works when reading in ADC value       
                    if val>3.3: 
                        return '0'
                    else:
                        return ['t',val]
                        #tag the value so then it can be stored in the appropriate matrix

#if __name__=='__main__':
# 
#    for i in range(0,50):
#
#    ser.close()