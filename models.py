#
# stores the header information from bulk file
# does not change after the record is created
#
class BulkHeader:
    totalAmount = 0
    line_no = 1


#
# stores the each transaction detail
# along with related WHT etc
# after creation only the status will change
#
class BulkTransaction:
    # values from the bulk file
    # does not change after creation
    line_no = 1
    refno = ''
    amount = 0
    hasWHT = False
    whtAmount = None
    value_date = None
    status = 'VALID' # valid, invalid, deleted etc
    errors = []


class WithHolindTax:
    line_no = 1
    whtAmount = 0


class Invoice:
    line_no = 1
    invAmount = 0


#
# summary record per file
# the bulk summary api will read from this record
#
class BulkSummary:
    header = BulkHeader()
    channel = 'WEB' # or SFTP
    bulk_type = 'PAYROLL1'
    uploaded_by = 'user1'
    filename = ""
    chksum = MD5 of file_content
    file_content = "BLOB"
    trans = None
    invoices = None
    unknown = None # lines in the file that have incorrect record type
    effectiveTotalAmount = 0 # effective total amount excluding deleted transactions
    status = 'PENDING' # validation in progress,
    errors = []


def generateBulk1():
    tran1 = BulkTransaction()
    trans1.refno = '1111'
    tran1.ammount = 10000
    tran1.hasWHT = False

    tran2 = BulkTransaction()
    tran2.ammount = 20000
    trans1.refno = '2222'
    tran2.hasWHT = True
    tran2.wht = WithHolindTax()
    tran2.wht.whtAmount = 1000

    header = BulkHeader()
    header.totalAmount = 30000

    bulk = BulkSummary()
    bulk.header = header
    bulk.trans = [tran1, tran2]

    return bulk


def validate_file(user, entitlement, file_path):
    # handled in upload microservice itself
    # 1. virus scan
    # 6. file size 25M
    # 7. file type, by using file extension

    bulk = generateBulk1() # should replace with file parsing logic

    # 2. duplicate,
    # search data of record with same checksum

    # 3. bulk file type
    # ???

    # 4. service subscription/onboarding
    # check if company subscribe to the service for bulk_type
    if not has_subscription(user.company, bulk.bulk_type):
        bulk.errors.append("company not sub to service")
        return False, bulk

    # 5. bulk type entitlement
    # check if user has entitlement for given transfer service
    if not has_entitlement(user, bulk.bulk_type):
        bulk.errors.append("user cannot perform transfer")
        return False, bulk

    # 8. file format...
    # how to check file format is new bulk?? is it even neccessary?

    # 9. company id
    if user.company <> bulk.company:
        bulk.errors.append("user company and bulk company mismatch")
        return False, bulk

    # 10. SFTP user id
    if bulk.channel == 'SFTP' and user.username is not valid:
        bulk.errors.append("invalid user")
        return False, bulk

    # 11. payment ref number
    # 1. refno unique
    if not is_detail_field_unique(bulk, "refno"):
        bulk.errors.append("refno not unique")
    # 2. each detail has a WHT,
    # flatten is done during parsing
    # loops through bulk.trans, for each record that has WHT True, check vvalue in WHT record
        bulk.errors.append("refno not unique")
    # 3. refno in WHT uniq
    if not is_detail_field_unique(bulk, "wht.refno"):
        bulk.errors.append("refno not unique")

    # 12. debit account
    # 1. same account
    account_set, _ = vals_for_field(bulk, "trans.debit_account_no")
    if account.size() <> 1:
        bulk.errors.append("not same debit account")
    # 2. debit account exists
    debit_account = account_set.get(0)
    if not is_debit_account_valid(debit_account):
        bulk.errors.append("not same debit account")
    # 3. user entitlement can use account
    if not has_entitlement(user, debit_account):
        bulk.errors.append("user does not have entitlement to use debit account")
    # 4. debit account type, status, etc are ok
    if not is_debit_account_eligible(debit_account):
        bulk.errors.append("account cannot be used")

    # 13. mandatory field in header
    # TODO: ..need a generic mechanism

    # 14. max number of records
    if len(bulk.trans) > 30000:
        bulk.errors.append("num of trans above max 30000")
    # TODO: what is bulk online??

    # 15. total payment record
    if bulk.total_trans_count <> len(bulk.trans):
        bulk.errors.append("total detail count does not match header")

    # 16. total payment amount
    if bulk.total_trans_count <> sum_of_field(bulk, "trans.amount")
        bulk.errors.append("total detail count does not match header")

    # 17. total WHT record
    if bulk.total_wht_count <> len(bulk.trans.wht):
        bulk.errors.append("total WHT count does not match header")

    # 18. total WHT amount
    if bulk.total_wht_count <> sum_of_field(bulk, "trans.wht.whtAmount")
        bulk.errors.append("total WHT amount does not match header")

    # 19. total invoice record
    if bulk.total_invoice_count <> len(bulk.trans.wht):
        bulk.errors.append("total invoice count does not match header")

    # 20. total invoice amount
    if bulk.total_invoice_count <> sum_of_field(bulk, "invoice.amount")
        bulk.errors.append("total invoice ammount does not match header")

    # 21. value date
    eff_date_set, _ = vals_for_field(bulk, "trans.effective_date")
    eff_dat = eff_date_set.get(0)
    # 1. not before today
    if eff_dat < now():
        bulk.errors.append("effective day cannot be before today")
    # 2. same effective date
    if eff_dat.size() <> 1:
        bulk.errors.append("different effective date in transaction records")
    # 3. effective date matches header
    if eff_date <> bulk.header.effective_date:
        bulk.errors.append("effective date in transaction does not match header day not same for all records")
    # 4. effective date availabe for service
    if not is_eff_date_valid_for_service(bulk.service_type):
        bulk.errors.append("effective date cannot be applied to service type")

    # 22. same debit day
    debit_date_set, _ = vals_for_field(bulk, "trans.debit_date")
    debit_dat = debit_date_set.get(0)
    if eff_dat.size() <> 1:
        bulk.errors.append("different debit date in transaction records")

# field validation utils
def is_detail_field_unique(bulk, expr):
    val_lst, val_set = vals_for_field(bulk, expr) # a set
    return val_lst.size() == val_set.size()

def sum_of_field(bulk, expr):
    _, val_lst = vals_for_field(bulk,expr)
    return sum(val_lst)

def vals_for_field(bulk, expr):
    iter, field = # split expr into iterable and remainder, e.g. trans.amount => iter=trans, filed=amount
    val_lst = [] # a list
    val_set = {} # a set
    for d in iter:
        val = get_value(d, field) # this is not valie code, just to illustrate
        val_set.add(val)
        val_lst.add(val)
    return val_lst, val_set

# invooke apis
def has_subscription(user.company, bulk.bulk_type):
    pass

def has_entitlement(user, bulk.bulk_type):
    pass

def is_debit_account_valid(debit_account):
    pass

def has_entitlement(user, debit_account):
    pass

def is_debit_account_eligible(debit_account):
    pass

if __name__ == "__main__":
    bulk1 = generateBulk1();
    print(bulk1)