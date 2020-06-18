from django import template
register = template.Library()

@register.filter
def check_purchase_status(lst, i):
    try:
        counter = 0
        for item in lst.iterator():            
            if i == item.product_id:
                if item.status == 1:
                    return lst[counter]
            counter += 1
        return lst[counter]    

    except:
        return None

@register.filter
def check_request_status(lst, i):
    try:
        counter = 0
        for request in lst.iterator():            
            if i == request.product_id:
                if not request.responded:
                    return lst[counter]
                else:
                    return lst[counter]    
            counter += 1
        return None    

    except Exception as e:
        print("HELLO",lst, e)
        return None        

@register.filter
def check_mentor_type(item):
    try:
        return item.request.product.name    
    except:
        return None                