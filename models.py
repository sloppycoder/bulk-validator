#
# stores the header information from bulk file
# does not change after the record is created
#
class BulkHeader:
    totalAmount = 0


#
# stores the each transaction detail
# along with related WHT etc
# after creation only the status will change
#
class BulkTransaction:
    # values from the bulk file
    # does not change after creation
    refno = ''
    amount = 0
    hasWHT = False
    whtAmount = None
    status = 'VALID' # valid, invalid, deleted etc
    errors = []


class WithHolindTax:
    whtAmount = 0


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
    tran1.ammount = 10000
    tran1.hasWHT = False

    tran2 = BulkTransaction()
    tran2.ammount = 20000
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
    if


def is_detail_filed_unique(field_name):
    val_set = Set()
    for d in bulk.trans:
        val_set.add(d.refno)

if __name__ == "__main__":
    bulk1 = generateBulk1();
    print(bulk1)