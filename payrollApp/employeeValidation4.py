'''
Created on 14 Jul 2020

@author: Marty
'''

from fpdf import FPDF
import datetime
import calendar
import os
from workalendar.europe import Ireland
from builtins import str


# ------------------ global variables 

# set of data structures for payroll file processing 
payrollKeys = ["pps", "fname", "sname", "mname", "dob","email",
               "prsi_class", "al_salary","al_srcop","al_paye_credits","al_pension_percent","cum_gp_to_date","cum_srcop",
               "cum_lwr_paye","cum_higher_paye","cum_tax_credits","cumulative_usc","cum_gross_tax","cum_tax_due"]

# list that holds an array of the values for each employee extracted from payroll file
payrollValuesData = []
# list that holds keys for values extracted
payrollKeyData = [] 
# dictionary that will hold key and values for one employee
payrollValuesDataDict = {}
# list of dictionaries with employees data
payrollDataFile = []
# list with updated values for payroll file 
payrollOutputsData = []
# set used to validate file against duplicates
ppsCheck = set()



# set of data structures for payslip file processing
uscKeys = ["pps", "fname", "sname", "mname","date_of_payment",
           "cum_gp_to_date", "gp_for_usc_this_period", "cum_usc_cut_off_point_1", "cum_usc_due_at_usc_rate_1", "cum_usc_cut_off_point_2",
           "cum_usc_due_at_usc_rate_2", "cum_usc_cut_off_point_3", "cum_usc_due_at_usc_rate_3", "cum_usc_due_at_usc_rate_4","cumulative_usc","usc_ded_this_period", "usc_ref_this_period"]
# list that holds an array of the usc card values for each employee extracted from usc card file
uscValuesData = []
# list that holds keys for values extracted
uscKeyData = []
# dictionary that will hold key and values for one employee
uscValuesDataDict = {}
# list of dictionaries with employees data for USC card
uscCardDataFileDict = {}
# list of dictionaries with employees data
uscDataFile = []
# list with updated values for usc card file 
uscCards = []


payslipsValuesDataDict = {}
payslips = []

'''
# set of data for TDC card creation
tdcKeys = ["pps", "fname", "sname", "mname", "dob",
           "al_salary","al_srcop","al_paye_credits","al_pension_percent","prsi_class","cum_gp_to_date","cum_srcop",
                 "cum_lwr_paye","cum_higher_paye","cum_tax_credits","email","cumulative_usc","cum_gross_tax","cum_tax_due"]
'''

tdcValuesDataDict = {}
tdcCards = []


# ------------------  end global variables

# debugging dates 
# 20102-6-16
# 2010-26-6
# 2010-6-56

# 2010-6-16
# 2021-6-16
# 2020-9-10
# 2020-09-10



# file path for application and files used for processing
destination = os.getcwd() + "\\EmploeePayslips\\"  
payrollFileInput = "payrollFile1.txt"
uscDataFileInpute = "uscData.txt"



# -------------- Welcome information

print("Welcome \nThis is Automated Payroll Application ")



# -------------- user data input validation -------------------------------------------------------

# input date of payment from administrator 
print("Provide data of payment in following format: Year, Month, Day")
inputDateOfPayment = input();



#------------- date validation for correct format -------------------------------------------------------------
isDateValid = False

def validateDataInput(date, isDateV):
    #print("This is your date ", date) # debug       
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        isDateV = bool(True)
    except ValueError:
        print("Incorrect data format, should be YYYY-MM-DD")
        print("Please try again ")
    return isDateV

isDateValid = validateDataInput(inputDateOfPayment, isDateValid)

while not isDateValid:   
    inputDateOfPayment = input();
    isDateValid = validateDataInput(inputDateOfPayment, isDateValid)  



#--------- past date validation -----------------

isPastDate = False

def pastDateCheck(date, isPD):
    if (datetime.date.today()) < (datetime.datetime.strptime(date, '%Y-%m-%d').date()):
        isPD = True
        print("This is not valid date\nPayroll can only be processed for future date in current tax year ")
        
    return isPD

isPastDate = pastDateCheck(inputDateOfPayment, isPastDate)


#-------- tax year validation --------------------
isCurrentTaxYear = False

def currentTaxYearCheck(date, isYearV):
    if (datetime.date.today()).year == (datetime.datetime.strptime(date, '%Y-%m-%d')).year:
        isYearV = True
        print("This is not valid date\nPayroll can only be processed for future date in current tax year ")
    return isYearV

isCurrentTaxYear = currentTaxYearCheck(inputDateOfPayment, isCurrentTaxYear)

while not (isCurrentTaxYear and isPastDate and  isDateValid):          
    isDateValid = False
    isPastDate = False
    isCurrentTaxYear = False    
    inputDateOfPayment = input();
    
    isDateValid = validateDataInput(inputDateOfPayment, isDateValid)             
    if isDateValid:
        isCurrentTaxYear = currentTaxYearCheck(inputDateOfPayment, isCurrentTaxYear)
        isPastDate = pastDateCheck(inputDateOfPayment, isPastDate)
           

#------- month number is extracted from data 
d = datetime.datetime.strptime(inputDateOfPayment, '%Y-%m-%d')
paydate = datetime.date(d.year,d.month,d.day)

monthOfpayment = d.month
monthName = calendar.month_name[monthOfpayment]





#-------- Function for check if day is not bank holiday
def isBankHolidayFunc(date):   
    for d in Ireland().holidays(date.year):
        if d[0] == date: return True           
    return False

# Function for check if day is not weekend day 
def isWeekendFunc(date):    
    if date.weekday() < 5:
        return False 
    else:
        return True

# Function for generating previous working day
def previousWorkingDay(date):
    return date - datetime.timedelta(max(1, (date.weekday() + 6) % 7 - 3))

# Payment date is validated and changed for previous available day if necessary 
while isBankHolidayFunc(paydate) or isWeekendFunc(paydate):
    #print(paydate, "is not bussines day") 
    paydate = previousWorkingDay(paydate)
#newPaydate = paydate
paydate = str(paydate)
print("This is not bussines day\nPaymant must be processed before this date \nPayment will be processed on -", paydate)




# Here prsi_ins_weeks for given month is calculated
week_count_per_month = {1:5, 2:9, 3:13, 4:18, 5:22, 6:26, 7:31, 8:35, 9:39, 10:44, 11:48, 12:52}

prsi_ins_weeks = week_count_per_month[monthOfpayment]



# -------------- end user data input validation -------------------------------------------------------


print("\n\n now extraction \n\n") # debugging


#######################################################################################################
# Data extraction module 
#######################################################################################################



## extracting data from payroll file and processing for further calculations
# check if file exists 
if payrollFileInput in os.listdir():
    #if exists open and  read file into the list
    with open(payrollFileInput, "r") as employeePayrollDate: 
        
        for i in employeePayrollDate.readlines():
            #print(type(i))
            data = i.split(",")
            #print(type(data))
            # check for double entry for one Employee
            if data[0] not in ppsCheck:
                print(data[0])
                ppsCheck.add(data[0])                
                payrollValuesData.append(data)          
            payrollKeyData.append(payrollKeys)
            #print(payrollValuesData)
        #print(payrollKeys)
        print(payrollKeyData)
        
        print("ppsCheck ",ppsCheck)
        
        
        ppsCheck = set()
        for k,v in zip(payrollKeyData, payrollValuesData):            
            for i in range(19):
                payrollValuesDataDict[k[i]] = v[i] 
                #print(k[i], " - ", v[i])           
            payrollDataFile.append(payrollValuesDataDict)
            #print(payrollValuesDataDict)
            payrollValuesDataDict = {}
    print("Payroll data processed")
else:
    print("Payroll data is missing")




#debug
for pd in payrollDataFile: 
    print((pd))
print("---------------------------------------")


#  extracting data from USC file

if uscDataFileInpute in os.listdir():
    #if exists open and  read file into the list
    with open(uscDataFileInpute, "r") as usdPayrollDate: 
        
        for j in usdPayrollDate.readlines():
            data1 = j.split(",")
            #print(data1)
            # check for double entry for one Employee
            if data1[0] not in ppsCheck:
                print(data1[0])
                ppsCheck.add(data1[0])
                uscValuesData.append(data1)          
            uscKeyData.append(uscKeys)
            
        print("uscValuesData ",uscValuesData)
        print("uscKeyData ",uscKeyData)
        print("ppsCheck ",ppsCheck)
        #print(uscValuesData)
        for k,v in zip(uscKeyData, uscValuesData):            
            for i in range(17):
                uscValuesDataDict[k[i]] = v[i] 
                print(k[i], " - ", v[i])           
            uscDataFile.append(uscValuesDataDict)
            print(uscValuesDataDict)
            uscValuesDataDict = {}
else:
    print("USCCard is missing")

print("")
# debug
for pc in uscDataFile: 
    print((pc))
print()










###############################################################################################
#  Process 2 -- calculation module
###############################################################################################



#def calculateAllValues():

print(" in caluclation ") # debugging

personalData = {"pps":"", "fname":"", "sname":"", "mname":"", "dob":"","email":"", "prsi_class":""}
monthlyCalculations = {} #{"mo_gross_pay_less_super":"", "date_of_payment":"", "prsi_ins_weeks":"", "prsi_ee":"", "prsi_er":"",  "usc_ded_this_period":"", "usc_ref_this_period":""} # , "mo_net_pay":""
uscMonthlyCalculations = {} #{ "date_of_payment":""}
cumulativeCalculations = {} #{"cum_gp_to_date":"", "cum_srcop":"", "cum_lwr_paye":"", "cum_higher_paye":"", "cumulative_usc":"", "cum_tax_credits":"", "cum_gross_tax":"", "cum_tax_due":""}
uscCumulativeCalculations = {} #{"gp_for_usc_this_period":"", "cum_gp_for_usc_to_date":"", "cum_usc_cut_off_point_1":"", "cum_usc_due_at_usc_rate_1":"", "cum_usc_cut_off_point_2":"", "cum_usc_due_at_usc_rate_2":"", "cum_usc_cut_off_point_3":"", "cum_usc_due_at_usc_rate_3":"", "cum_usc_due_at_usc_rate_4":""}         


for pd,us in zip(payrollDataFile, uscDataFile):                
    #print(pd)   
    for key in personalData:
        #print(key)
        if key in pd:
            personalData[key] = pd[key]
            #print(pd[key])
    print((personalData))
    
    payslipsValuesDataDict.update(personalData)    
    tdcValuesDataDict.update(personalData)
    tdcValuesDataDict.pop("dob")
    uscValuesDataDict.update(personalData)    
    
    
    payrollValuesDataDict.update(personalData)
       
    payrollValuesDataDict["al_salary"] = (pd["al_salary"])
    payrollValuesDataDict["al_srcop"] = (pd["al_srcop"])
    payrollValuesDataDict["al_paye_credits"] = (pd["al_paye_credits"])
    payrollValuesDataDict["al_pension_percent"] = (pd["al_pension_percent"])
    
    #      total_Cut-Off_Point      tax_Rate 1    tax_Rate 2    taxYear
    tdcValuesDataDict["al_paye_credits"] = (pd["al_paye_credits"])
    tdcValuesDataDict["total_Cut-Off_Point"] = "20%"
    tdcValuesDataDict["tax_Rate_1"] = "20%"
    tdcValuesDataDict["tax_Rate_2"] = "40%"
    tdcValuesDataDict["taxYear"] = str(paydate[:4])
    tdcValuesDataDict["employerName"] = "ICTAP Resourcing Ltd."
    tdcValuesDataDict["employerNumber"] = "Er. No. 1234567Y"
     
        
    
   
    
            
    annualSalary = float(pd["al_salary"])
    pension = (annualSalary * 0.02)/12    
    monthlySalary = (annualSalary/12)
    #print(annualSalary , " -- ",  monthlySalary)     
    
    monthlySalaryLessPension = monthlySalary - pension
    
    
    monthlyCalculations["mo_gross_pay_less_super"] = "%.2f" %(monthlySalaryLessPension)
    monthlyCalculations["date_of_payment"] = paydate
    uscValuesDataDict["date_of_payment"] = paydate
    monthlyCalculations["prsi_ins_weeks"] = "%.2f" %(5) 
    tdcValuesDataDict["cumulative_Cut-Off_Point"] = "%.2f" %(monthlySalaryLessPension)
    #uscValuesDataDict["mo_gross_pay_less_super"] = "%.2f" %(monthlySalaryLessPension)
    uscValuesDataDict.pop("dob")
    uscValuesDataDict.pop("email")
    uscValuesDataDict.pop("prsi_class")
    
    
    
    
    #---------- Pay Tax calculation
        
    annualScrop = float(pd["al_srcop"])
    annualTaxCredit = float(pd["al_paye_credits"])
    monthlyTaxCredit = annualTaxCredit/12
    totalMonthlyPayeTax = 0
    monthlyScrop = 0
    
    if annualScrop > annualSalary:
        
        monthlyScrop = annualSalary/12
        twentyPercent = (monthlyScrop) * 0.2
        fortyPercent = (monthlySalaryLessPension - monthlyScrop) * 0.4
        if fortyPercent <= 0: fortyPercent = 0
        
        totalMonthlyPayeTax = (twentyPercent + fortyPercent) - monthlyTaxCredit        
        if totalMonthlyPayeTax <= 0: totalMonthlyPayeTax = 0
        
    else:
        monthlyScrop = annualScrop/12
        twentyPercent = (monthlyScrop) * 0.2
        fortyPercent = (monthlySalaryLessPension - monthlyScrop) * 0.4
        
        totalMonthlyPayeTax = twentyPercent + fortyPercent - monthlyTaxCredit
        
    #print(totalMonthlyPayeTax)

    #------------ PRSI calculation   
 
    prsiEE = monthlySalary * 0.04    
    prsiER = monthlySalary * 0.1095    
    totalMonthlyPRSITax = prsiEE + prsiER    
    
    
    tdcValuesDataDict["total_tax_this_period_deducted"] = "%.2f" %(totalMonthlyPayeTax)
    tdcValuesDataDict["total_tax_this_period_refund"] = "%.2f" %(0)
    tdcValuesDataDict["total_PRSI"] = "%.2f" %(totalMonthlyPRSITax)
    
    monthlyCalculations["prsi_ee"] = "%.2f" %(prsiEE)
    monthlyCalculations["prsi_er"] = "%.2f" %(prsiER)

    uscRate1 = 0
    uscRate2 = 0
    uscRate3 = 0
    uscRate4 = 0
    # USC calculation 
    if annualSalary < 12012: pass
    if annualSalary > 12012: uscRate1 = (12012/12) * 0.005
    if annualSalary < 20484 and annualSalary >= 12012: uscRate2 = ((8472 - (20484 - annualSalary))/12) * 0.02 
    if annualSalary >= 20484 : uscRate2 = (8472 / 12) * 0.02  
    if annualSalary < 70044 and annualSalary >= 20484: uscRate3 = ((monthlySalaryLessPension - (19873.992 /12)) * 0.045 ) 
    if annualSalary > 70044 : uscRate3 = (49560.01 / 12) * 0.045  
    if annualSalary >= (70044): uscRate4 = (annualSalary/12) * 0.08
        
    totalMonthlyUSC = uscRate1 + uscRate2 + uscRate3 + uscRate4    
    #print(uscRate1, "  " , uscRate2, "  " ,  uscRate3 , "  " ,  uscRate4)
    
    gp_for_usc_this_period = float(us["gp_for_usc_this_period"])
    
    
    
    
    
    
    
    cum_gp_to_date = float(us["cum_gp_to_date"]) 
    uscCumulativeCalculations["cum_gp_to_date"] = str("%.2f" %(cum_gp_to_date + monthlySalaryLessPension))
    
    monthlyCalculations["usc_ded_this_period"] = "%.2f" %(totalMonthlyUSC)
    
    
    
    uscDeductedThisPeriod = "%.2f" %(totalMonthlyUSC)
    uscRefoundedThisPeriod = ""
    
    if totalMonthlyUSC > 0: 
        monthlyCalculations["usc_ref_this_period"] = "%.2f" %(0)
        uscRefoundedThisPeriod = "%.2f" %(0)
    else:
        monthlyCalculations["usc_ref_this_period"] = "%.2f" %(totalMonthlyUSC) 
        uscRefoundedThisPeriod = "%.2f" %(totalMonthlyUSC)
    
    totalDedactions = totalMonthlyPayeTax +  prsiEE  + totalMonthlyUSC 
    #print(totalDedactions)
    
    netMonthlySalary = monthlySalaryLessPension - totalDedactions    
    monthlyCalculations["mo_net_pay"] = "%.2f" %(netMonthlySalary)
    
    print("hestresef")
   
    cum_gp_to_date = float(pd["cum_gp_to_date"]) 
    cumulativeCalculations["cum_gp_to_date"] = "%.2f" %(cum_gp_to_date + monthlySalary)
    
    gpForUSCthisPeriond = "%.2f" %(monthlySalaryLessPension)
    uscCumulativeCalculations["gp_for_usc_this_period"] = str(gpForUSCthisPeriond)  
    
    uscValuesDataDict["cum_gp_to_date"] = "%.2f" %(cum_gp_to_date + monthlySalary)
    uscCardDataFileDict.update(uscValuesDataDict)
    
    cum_srcop = float(pd["cum_srcop"]) 
    cumulativeCalculations["cum_srcop"] = "%.2f" %(cum_srcop + monthlyScrop)
    
    cum_lwr_paye = float(pd["cum_lwr_paye"]) 
    cumulativeCalculations["cum_lwr_paye"] = "%.2f" %(cum_lwr_paye + twentyPercent)
    
    cum_higher_paye = float(pd["cum_higher_paye"]) 
    cumulativeCalculations["cum_higher_paye"] = "%.2f" %(cum_higher_paye + fortyPercent)
    
    cumulative_usc = float(pd["cumulative_usc"]) 
    cumulativeCalculations["cumulative_usc"] = "%.2f" %(cumulative_usc + totalMonthlyUSC)
        
    cum_tax_credits = float(pd["cum_tax_credits"]) 
    cumulativeCalculations["cum_tax_credits"] = "%.2f" %(cum_tax_credits + monthlyTaxCredit)
    
    cum_gross_tax = float(pd["cum_gross_tax"]) 
    cumulativeCalculations["cum_gross_tax"] = "%.2f" %(cum_gross_tax + totalDedactions) # wyjasinic co znaczy gross tax
    
    cum_tax_due = float(pd["cum_tax_due"]) 
    cumulativeCalculations["cum_tax_due"] = "%.2f" %(cum_tax_due + totalMonthlyPayeTax)    
    
   
    
    uscHeaderValuesDict={}
     
    uscHeaderValuesDict["USC Cut-Off Point 1"] = "12012" 
     
    uscHeaderValuesDict["USC Cut-Off Point 1"] = "12012"
    uscHeaderValuesDict["USC Cut-Off Point 2"] = "19874"
    uscHeaderValuesDict["USC Cut-Off Point 3"] = "70044"
    
    uscHeaderValuesDict["taxYear"] = str(paydate[:4])
    uscHeaderValuesDict["employerName"] = "ICTAP Resourcing Ltd."
    uscHeaderValuesDict["employerNumber"] = "Er. No. 1234567Y" 
       
    
    uscHeaderValuesDict["USC Rate 1"] = "0.5%"
    uscHeaderValuesDict["USC Rate 2"] = "2%"
    uscHeaderValuesDict["USC Rate 3"] = "4.5%"
    uscHeaderValuesDict["USC Rate 4"] = "8%"
        
    
    
    
    cum_usc_cut_off_point_1 = float(us["cum_usc_cut_off_point_1"]) + 100 
    uscCumulativeCalculations["cum_usc_cut_off_point_1"] = str("%.2f" %(cum_usc_cut_off_point_1))    
    
    cum_usc_due_at_usc_rate_1 = float(us["cum_usc_due_at_usc_rate_1"]) + 100    
    uscCumulativeCalculations["cum_usc_due_at_usc_rate_1"] = str("%.2f" %(cum_usc_due_at_usc_rate_1))
    
    cum_usc_cut_off_point_2 = float(us["cum_usc_cut_off_point_2"]) + 100 
    uscCumulativeCalculations["cum_usc_cut_off_point_2"] = str("%.2f" %(cum_usc_cut_off_point_2))
    
    cum_usc_due_at_usc_rate_2 = float(us["cum_usc_due_at_usc_rate_2"]) + 100    
    uscCumulativeCalculations["cum_usc_due_at_usc_rate_2"] = str("%.2f" %(cum_usc_due_at_usc_rate_2))
    
    cum_usc_cut_off_point_3 = float(us["cum_usc_cut_off_point_3"]) + 100 
    uscCumulativeCalculations["cum_usc_cut_off_point_3"] = str("%.2f" %(cum_usc_cut_off_point_3))    
    
    
    cum_usc_due_at_usc_rate_3 = float(us["cum_usc_due_at_usc_rate_3"]) + 100    
    uscCumulativeCalculations["cum_usc_due_at_usc_rate_3"] = str("%.2f" %(cum_usc_due_at_usc_rate_3))
    
    cum_usc_due_at_usc_rate_4 = float(us["cum_usc_due_at_usc_rate_1"]) + 100    
    uscCumulativeCalculations["cum_usc_due_at_usc_rate_4"] = str("%.2f" %(cum_usc_due_at_usc_rate_4))
        
    uscCumulativeCalculations["cumulative_usc"] = "%.2f" %(cumulative_usc + totalMonthlyUSC) 
    
    uscCumulativeCalculations["usc_ded_this_period"] = uscDeductedThisPeriod
    
    uscCumulativeCalculations["usc_ref_this_period"] = uscRefoundedThisPeriod
    
    
    
    
    payslipsValuesDataDict.update(cumulativeCalculations)
    payslipsValuesDataDict.update(monthlyCalculations)
    payslipsValuesDataDict["pension"] = "%.2f" %(pension)
    payslips.append(payslipsValuesDataDict)
    payslipsValuesDataDict = {}
        
    
    tdcValuesDataDict.update(cumulativeCalculations)  
    tdcValuesDataDict["cumulative_Cut-Off_Point"] = "%.2f" %(monthlyScrop * monthOfpayment)  
    tdcValuesDataDict.update(monthlyCalculations)
    tdcValuesDataDict["prsi_class"] = (pd["prsi_class"])
    tdcValuesDataDict["prsi_ins_weeks"] = str(prsi_ins_weeks)
    tdcCards.append(tdcValuesDataDict)
    tdcValuesDataDict = {}  
    
    
    
    uscCardDataFileDict.update(uscHeaderValuesDict)
    uscCardDataFileDict.update(uscMonthlyCalculations)
    uscCardDataFileDict.update(uscCumulativeCalculations)
    uscCards.append(uscCardDataFileDict)
    uscCardDataFileDict = {}
    
    
    
    print("")
    print("NOW 2020-10-10  ", uscCards)
    print("")
    
    
    
        
    payrollValuesDataDict["prsi_class"] = (pd["prsi_class"])
    payrollValuesDataDict.update(cumulativeCalculations)    
    
    payrollOutputsData.append(payrollValuesDataDict)
    payrollValuesDataDict = {}


    #uscCardDataFile.append(uscHeaderValuesDict)
    #uscCardDataFile.append(uscValuesDataDict)

    print("Before ---- ",uscDataFile)
    uscDataFile=[]
    #uscValuesDataDict.update(uscMonthlyCalculations)
    uscValuesDataDict.update(uscCumulativeCalculations)    
    uscDataFile.append(uscValuesDataDict)    
    uscValuesDataDict = {}
    print("After-------", uscDataFile)
    
    
#calculateAllValues()


###########################################################################
######### --- end of calculation ------------------------------------------
###########################################################################






print(" now payslip creation ") # debugging




# class for Pdf payslip template ---------------------------------------------------------------------
class payslipPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'BU', 12)

    # Page footer
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 6)
        self.cell(0, 10, 'ICTAP Resourcing Ltd.  ( Er. No. 1234567Y  ) ', 0, 0, 'C')     




# this function create payslip -------------------------------------------------------------------------
def createPayslip(empName, month, payslip):
    
         
    col1 = ['{:60s} {:12s}'.format("PPS Number", payslip['pps']),
            '{:67s} {:12s}'.format("Date", paydate),
            '{:66s} {:12s}'.format("Gross Salary", payslip['mo_gross_pay_less_super']),
            '{:60s} {:12s}'.format("", ""),
            '{:60s} {:12s}'.format("", ""),
            '{:60s} {:12s}'.format("", ""),
            '{:67s} {:12s}'.format("Net Pay", payslip['mo_net_pay']),
            '{:60s} {:12s}'.format("YTD Gross Pay", payslip['cum_gp_to_date']),
            '{:65s} {:12s}'.format("SCROP", payslip['cum_srcop']),
            '{:60s} {:12s}'.format("Gross Tax Due", payslip['cum_gross_tax']),
            '{:66s} {:12s}'.format("Tax Credits", payslip['cum_tax_credits']),
            '{:60s} {:12s}'.format("", "")]
          
    col2 = ['{:60s} {:12s}'.format("DOB", payslip['dob']),
            '{:60s} {:12s}'.format("", ""),
            '{:66s} {:12s}'.format("Pension", payslip['pension']),
            '{:68s} {:12s}'.format("Paye", payslip['mo_gross_pay_less_super']),
            '{:60s} {:12s}'.format("", ""),
            '{:60s} {:12s}'.format("", ""),
            '{:67s} {:12s}'.format("Net Pay", payslip['mo_net_pay']),
            '{:60s} {:12s}'.format("YTD Gross Pay", payslip['cum_gp_to_date']),
            '{:65s} {:12s}'.format("SCROP", payslip['cum_srcop']),
            '{:61s} {:12s}'.format("Gross Tax Due", payslip['cum_gross_tax']),
            '{:68s} {:12s}'.format("Class", payslip['prsi_class']),
            '{:60s} {:12s}'.format("USC Deducted", payslip['usc_ded_this_period'])]  
          
    
    pdf = payslipPDF('P','mm', (200,120))    
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.cell(0, 10, 'Payslip for ' + empName, 0, 0, 'C')
    pdf.set_font('Times', '', 8)
    pdf.ln(10)
    pdf.line(10, 22, 180, 22)
    pdf.line(10, 35, 180, 35)
    pdf.line(10, 65, 180, 65)
    pdf.line(10, 95, 180, 95)
    
    
    for i in range( len(col1)):    
                
                pdf.cell(1, 6, ' ' , 0, 1)
                pdf.cell(5)
                pdf.cell(0, 0, col1[i], 0, 1)
                pdf.cell(100)
                pdf.cell(0, 0, col2[i] , 0, 1)
                             
    
    pdf.output(destination + empName+"\\Payslips\\" + str(month) + '.pdf', "F")
    
    








    
    
# this function create tdc Card for new year or new employee 
def createTDCCardFile(empName, tdcCard, tdcCardFile):    
       
    employeeTDCRecord = " Tax Deduction Card \n ------------------ \n Employee Name         " + empName + "                                      Total Tax Credit " + tdcCard['al_paye_credits'] +    "                       Initial PRSI Class " + tdcCard['prsi_class'] + "\n\n" 
    employeeTDCRecord = employeeTDCRecord + " PPS Number            " + tdcCard['pps'] +    "                                        Total Cut-Off Point " + tdcCard['al_paye_credits'] + "  \n\n          "
    employeeTDCRecord = employeeTDCRecord + "                                                             Tax Rate 1 20%        Tax Rate 2 40%  \n\n  "
    employeeTDCRecord = employeeTDCRecord + "                                                                     Tax Year "  + tdcCard['taxYear'] + " \n\n"          
    employeeTDCRecord = employeeTDCRecord + " Employer Name         "  + tdcCard['employerName'] + "                  Employer Number "  + tdcCard['employerNumber'] + "  \n\n"  
    employeeTDCRecord = employeeTDCRecord + "--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    employeeTDCRecord = employeeTDCRecord + "      |  Date of |   Gross  | Cumulative | Cumulative | Cumulative | Cumulative |Cumulative|Cumulative|Cumulative|Tax Deducted|Tax Refunded|USC Deducted|USC Refunded|Insurable| PRSI  | PRSI   | Total  |   Net    |\n" 
    employeeTDCRecord = employeeTDCRecord + " Month|  Payment | Pay this | Gross Pay  |   Cut-Off  | Tax Due at | Tax Due at |  Gross   |Tax Credit|    Tax   |this Period | this period| this Period| this Period|  weeks  | class |Employee|  PRSI  |   Pay    |\n" 
    employeeTDCRecord = employeeTDCRecord + "      |  Payment |  period  |  to Date   |    Point   | Tax Rate 1 | Tax Rate 2 |   Tax    |  Monthly |          |            |            |            |            |         |       |  Share |        |          |\n"
    employeeTDCRecord = employeeTDCRecord + "--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    
    employeeTDCRecord = employeeTDCRecord + ('   {:3s}{:s}'.format(str(monthOfpayment),'|')) + ('{:10s}{:s}'.format(tdcCard['date_of_payment'],'|')) + (' {:9s}{:s}'.format(tdcCard['mo_gross_pay_less_super'],'|')) #+ 
    employeeTDCRecord = employeeTDCRecord + (' {:11s}{:s}'.format(tdcCard['cum_gp_to_date'],'|')) + (' {:11s}{:s}'.format(tdcCard['cumulative_Cut-Off_Point'],'|'))  + (' {:11s}{:s}'.format(tdcCard['cum_lwr_paye'],'|')) + (' {:11s}{:s}'.format(tdcCard['cum_higher_paye'],'|')) 
    employeeTDCRecord = employeeTDCRecord + (' {:9s}{:s}'.format(tdcCard['cum_gross_tax'],'|')) + (' {:9s}{:s}'.format(tdcCard['cum_tax_credits'],'|')) + (' {:9s}{:s}'.format(tdcCard['cum_tax_due'],'|')) + (' {:11s}{:s}'.format(tdcCard['total_tax_this_period_deducted'],'|')) 
    employeeTDCRecord = employeeTDCRecord + (' {:11s}{:s}'.format(tdcCard['total_tax_this_period_refund'],'|')) + (' {:11s}{:s}'.format(tdcCard['usc_ded_this_period'],'|')) + (' {:11s}{:s}'.format(tdcCard['usc_ref_this_period'],'|')) + (' {:8s}{:s}'.format(tdcCard['prsi_ins_weeks'],'|'))  
    employeeTDCRecord = employeeTDCRecord + (' {:6s}{:s}'.format(tdcCard['prsi_class'],'|')) + (' {:7s}{:s}'.format(tdcCard['prsi_ee'],'|')) + (' {:7s}{:s}'.format(tdcCard['total_PRSI'],'|')) +  (' {:9s}{:s}'.format(tdcCard['mo_net_pay'],'|')) + "\n" 
    employeeTDCRecord = employeeTDCRecord + "--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"

    # tdc card is written to file
    tdcCardFile.write(employeeTDCRecord)
    tdcCardFile.close()
    # record cleared
    employeeTDCRecord = ""

    
# This function is for updating already existing tdc cards 
def updateTDCCardFile(empName, tdcCard): 
        
    employeeTDCRecord =  ('   {:3s}{:s}'.format(str(monthOfpayment),'|')) + ('{:10s}{:s}'.format(tdcCard['date_of_payment'],'|')) + (' {:9s}{:s}'.format(tdcCard['mo_gross_pay_less_super'],'|'))  
    employeeTDCRecord = employeeTDCRecord + (' {:11s}{:s}'.format(tdcCard['cum_gp_to_date'],'|')) + (' {:11s}{:s}'.format(tdcCard['cumulative_Cut-Off_Point'],'|'))  + (' {:11s}{:s}'.format(tdcCard['cum_lwr_paye'],'|')) + (' {:11s}{:s}'.format(tdcCard['cum_higher_paye'],'|')) 
    employeeTDCRecord = employeeTDCRecord + (' {:9s}{:s}'.format(tdcCard['cum_gross_tax'],'|')) + (' {:9s}{:s}'.format(tdcCard['cum_tax_credits'],'|')) + (' {:9s}{:s}'.format(tdcCard['cum_tax_due'],'|')) + (' {:11s}{:s}'.format(tdcCard['total_tax_this_period_deducted'],'|')) 
    employeeTDCRecord = employeeTDCRecord + (' {:11s}{:s}'.format(tdcCard['total_tax_this_period_refund'],'|')) + (' {:11s}{:s}'.format(tdcCard['usc_ded_this_period'],'|')) + (' {:11s}{:s}'.format(tdcCard['usc_ref_this_period'],'|')) + (' {:8s}{:s}'.format(tdcCard['prsi_ins_weeks'],'|'))  
    employeeTDCRecord = employeeTDCRecord + (' {:6s}{:s}'.format(tdcCard['prsi_class'],'|')) + (' {:7s}{:s}'.format(tdcCard['prsi_ee'],'|')) + (' {:7s}{:s}'.format(tdcCard['total_PRSI'],'|')) +  (' {:9s}{:s}'.format(tdcCard['mo_net_pay'],'|')) + "\n" 
    employeeTDCRecord = employeeTDCRecord + "--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"

     
    tdcCardFile = open(destination + empName+"\\TDCcard.txt","a") 
    tdcCardFile.write(employeeTDCRecord)
    tdcCardFile.close()






# this function create tdc Card for new year or new employee 
def createUSCCardFile(empName, uscCard, uscCardFile):    
     
     
    print("this is usc card " , uscCard)
     
     
       
    employeeUSCRecord = " Universal Social Charge (USC) Payroll Card \n ------------------ \n Employee Name         " + empName + "                                     USC Cut-Off Point 1     " + uscCard["USC Cut-Off Point 1"] +                                    "\n\n" 
    employeeUSCRecord = employeeUSCRecord + " PPS Number            2131330K                                       USC Cut-Off Point 2     " + uscCard["USC Cut-Off Point 2"] + "  \n\n " 
    employeeUSCRecord = employeeUSCRecord + "                                                                     USC Cut-Off Point 3     " + uscCard["USC Cut-Off Point 3"] + "  \n\n"
    employeeUSCRecord = employeeUSCRecord + "                                                                      Tax Year                "  + uscCard["taxYear"] + " \n\n" 
    employeeUSCRecord = employeeUSCRecord + "                                                                      USC Rate 1    "  + uscCard["USC Rate 1"] + "    USC Rate 2    "  + uscCard["USC Rate 2"] + "    USC Rate 3    "  + uscCard["USC Rate 3"] + "    USC Rate 4   "  + uscCard["USC Rate 4"] + "\n\n"          
    employeeUSCRecord = employeeUSCRecord + " Employer Name         "  + uscCard["employerName"] + "                          Employer Number         "  + uscCard["employerNumber"] + "  \n\n"  
    employeeUSCRecord = employeeUSCRecord + "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    employeeUSCRecord = employeeUSCRecord + "      |  Date of |   Gross  | Cumulative | Cumulative  |Cumulative USC| Cumulative |Cumulative USC| Cumulative|Cumulative USC|Cumulative USC|Cumulative|USC Deducted|USC Refunded|\n" 
    employeeUSCRecord = employeeUSCRecord + " Month|  Payment | Pay this | Gross Pay  | USC Cut-Off |  Due at USC  |USC Cut-Off |  Due at USC  |USC Cut-Off|  Due at USC  |  Due at USC  |    USC   | this Period| this Period|\n" 
    employeeUSCRecord = employeeUSCRecord + "      |          |  period  |  to Date   |    Point 1  |    Rate 1    |   Point 2  |    Rate 2    |  Point 3  |    Rate 3    |    Rate 4    |          |            |            |\n"
    employeeUSCRecord = employeeUSCRecord + "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    
    employeeUSCRecord = employeeUSCRecord + ('   {:3s}{:s}'.format(str(monthOfpayment),'|')) + ('{:10s}{:s}'.format(uscCard['date_of_payment'],'|')) + (' {:9s}{:s}'.format(uscCard['gp_for_usc_this_period'],'|'))  
    employeeUSCRecord = employeeUSCRecord + (' {:11s}{:s}'.format(uscCard['cum_gp_to_date'],'|')) + (' {:12s}{:s}'.format(uscCard['cum_usc_cut_off_point_1'],'|'))  + (' {:13s}{:s}'.format(uscCard['cum_usc_due_at_usc_rate_1'],'|')) + (' {:11s}{:s}'.format(uscCard['cum_usc_cut_off_point_2'],'|')) 
    employeeUSCRecord = employeeUSCRecord + (' {:13s}{:s}'.format(uscCard['cum_usc_due_at_usc_rate_2'],'|')) + (' {:10s}{:s}'.format(uscCard['cum_usc_cut_off_point_3'],'|')) + (' {:13s}{:s}'.format(uscCard['cum_usc_due_at_usc_rate_3'],'|')) + (' {:13s}{:s}'.format(uscCard['cum_usc_due_at_usc_rate_4'],'|')) 
    employeeUSCRecord = employeeUSCRecord + (' {:9s}{:s}'.format(uscCard['cumulative_usc'],'|')) + (' {:11s}{:s}'.format(uscCard['usc_ded_this_period'],'|')) + (' {:11s}{:s}'.format(uscCard['usc_ref_this_period'],'|')) + "\n" 
    employeeUSCRecord = employeeUSCRecord + "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"


    #print(employeeUSCRecord)

    # tdc card is written to file
    uscCardFile.write(employeeUSCRecord)
    uscCardFile.close()
    # record cleared
    employeeUSCRecord = ""
    
    
    #print(employeeUSCRecord)
    





# This function is for updating already existing tdc cards 
def updateUSCCardFile(empName, uscCard): 


    employeeUSCRecord =  ('   {:3s}{:s}'.format(str(monthOfpayment),'|')) + ('{:10s}{:s}'.format(uscCard['date_of_payment'],'|')) + (' {:9s}{:s}'.format(uscCard['gp_for_usc_this_period'],'|'))   
    employeeUSCRecord = employeeUSCRecord + (' {:11s}{:s}'.format(uscCard['cum_gp_to_date'],'|')) + (' {:12s}{:s}'.format(uscCard['cum_usc_cut_off_point_1'],'|'))  + (' {:13s}{:s}'.format(uscCard['cum_usc_due_at_usc_rate_1'],'|')) + (' {:11s}{:s}'.format(uscCard['cum_usc_cut_off_point_2'],'|')) 
    employeeUSCRecord = employeeUSCRecord + (' {:13s}{:s}'.format(uscCard['cum_usc_due_at_usc_rate_2'],'|')) + (' {:10s}{:s}'.format(uscCard['cum_usc_cut_off_point_3'],'|')) + (' {:13s}{:s}'.format(uscCard['cum_usc_due_at_usc_rate_3'],'|')) + (' {:13s}{:s}'.format(uscCard['cum_usc_due_at_usc_rate_4'],'|')) 
    employeeUSCRecord = employeeUSCRecord + (' {:9s}{:s}'.format(uscCard['cumulative_usc'],'|')) + (' {:11s}{:s}'.format(uscCard['usc_ded_this_period'],'|')) + (' {:11s}{:s}'.format(uscCard['usc_ref_this_period'],'|')) + "\n" 
    employeeUSCRecord = employeeUSCRecord + "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"


     
    uscCardFile = open(destination + empName+"\\UCDcard.txt","a") 
    uscCardFile.write(employeeUSCRecord)
    uscCardFile.close()








# function for validating employees and creating file structure for them
def valideteEmployee(monthN, empName, payslip, uscCard, tdcCard):
    
    print(" teras tu jeste ",  uscCard['gp_for_usc_this_period'])
    
    previousPayslipNumber = monthN - 1
    if empName in os.listdir('EmploeePayslips/'):    
        if str(monthN) +'.pdf' in os.listdir("EmploeePayslips/" + empName + "/Payslips"):
            print("Documenets for this period have been generated - Please check data files")
        elif (str(previousPayslipNumber) +'.pdf' not in os.listdir("EmploeePayslips/" + empName + "/Payslips")) and (previousPayslipNumber > 1):
            print("Error!!!\nMissing previous payslip for",empName, "\nPaymant cannot be processed util records are not verified\nPlease check record and run program again" )
        
        
        
        else:
            
            print()
            createPayslip(empName, monthN, payslip)
            updateTDCCardFile(empName, tdcCard)
            updateUSCCardFile(empName, uscCard)
            
    else:
        print(("New employee " + empName))
        print(("File directory will be created " + empName))
        # file structure for new employee is created
        os.mkdir(destination + empName+"\\")       
        os.mkdir(destination + empName+"\\Payslips")     
        tdcCardFile = open(destination + empName+"\\TDCcard.txt","w")    
        uscCardFile = open(destination + empName+"\\UCDcard.txt","w")


        createPayslip(empName, monthN, payslip)
        createTDCCardFile(empName, tdcCard, tdcCardFile)
        createUSCCardFile(empName, uscCard, uscCardFile)


        







# ------------  Here whole calculation starts - main process ----------------

for num in range(len(payrollDataFile)):
    
    print("tu jestem ", len(payrollDataFile) , " num ", num )
    
    employeeName =  payrollDataFile[num]["fname"]+ " " + payrollDataFile[num]["mname"] + " " + payrollDataFile[num]["sname"]
    print(employeeName, )    
        
    print(" teras tu jeste ", monthOfpayment, employeeName , len(payslips) , len(tdcCards) , len(uscCards) )#, uscCards[num], tdcCards[num])
    
    # validation function is called. This function calls the function that produces Payslip, Usc and Tdc cards
    valideteEmployee(monthOfpayment, employeeName, payslips[num], uscCards[num], tdcCards[num])            

       


# update payroll file
    
employeePayrollDate = open("payrollFile1.txt", "w")
employeeRecord = ""
for emp in payrollOutputsData:
    #print(emp) # debugging
    employeeRecord = employeeRecord  + emp["pps"] 
    for k in emp:
        if k is not"pps":
            #print(emp[k])
            employeeRecord = employeeRecord + "," + emp[k] 
            #payrollOutputValues.append(emp[k])
    #print() # debugging
    #print(type(employeeRecord)) # debugging
    #print(employeeRecord)    # debugging
    employeeRecord = employeeRecord + "\n"
    employeePayrollDate.write(employeeRecord)
    employeeRecord = ""
employeePayrollDate.close()



#uscDataFile
print("555555555555555555555555555555555555555555555")
print("555555555555555555555555555555555555555555555")
print("555555555555555555555555555555555555555555555")
print("555555555555555555555555555555555555555555555\n\n\n")



usdPayrollDate = open("uscData.txt", "w")
employeeRecord = ""

for emp in uscDataFile:
    #print(emp) # debugging
    employeeRecord = employeeRecord  + emp["pps"] 
    for k in emp:
        if k is not"pps":
            #print(emp[k])
            employeeRecord = employeeRecord + "," + emp[k] 
            print(k + "   -  " + emp[k])
            #payrollOutputValues.append(emp[k])
    print() # debugging
    print(type(employeeRecord)) # debugging
    print(employeeRecord)    # debugging
    employeeRecord = employeeRecord + "\n"
    usdPayrollDate.write(employeeRecord)
    employeeRecord = ""
usdPayrollDate.close()





'''

print(" ------ Payroll file -------")           
for pd in payrollDataFile:    
    print(pd)       
          
            
print(" ------ Payslip file -------")             
for pl in payslips: 
    print(pl) 
    #createPayslip(empName, monthN)
            
            
print(" ------ tcd card file -------")               
for tc in tdcCards:           
    print(tc)             
print(" ------ usc card file -------")             
for uc in uscCards:           
    print(uc)             
            
print(" ------ Payroll output card file -------")             
for pr in payrollOutputsData:           
    print(pr)            
'''            
           
            
            
            
#>>>>>>> branch 'master' of https://github.com/czarny25/PayrollProject.git
            
            
            
            
            
            
            
            
            
            
            
            
            