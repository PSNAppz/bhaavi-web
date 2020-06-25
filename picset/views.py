from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from accounts.models import *
from django.http import JsonResponse
from django.contrib import messages
from collections import Counter 
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

@login_required(login_url='login')
def takeTest(request):
    if not request.user.customer:
        messages.warning(request, 'You are not a customer!')
        return redirect('dashboard')
    
    user_purchase = UserPurchases.objects.filter(user_id = request.user.id).filter(product_id = "PROD-1").get(status=True)
    last_q = Question.objects.last()
    try:
        answer = QuestionAnswer.objects.filter(purchase_id=user_purchase.id).order_by('question_id').last()
        question = Question.objects.get(pk=answer.question_id)
        if last_q.id == answer.question_id:
            context = {'question':question,'answer':answer,'final':True}  
        else:    
            context = {'question':question,'answer':answer,'final':False}  
        return render(request, 'picset/test.html',context)
    except:
        question = Question.objects.get(pk=1)
        answer = None    
        context = {'question':question,'answer':answer,'final':False}  
        return render(request, 'picset/test.html',context)

@login_required(login_url='login')
def getQuestion(request):
    if request.method == 'POST':
        try:
            #Save this QA
            question_id = int(request.POST['question_id'])
            prev = int(request.POST['previous'])
            submit = int(request.POST['submit'])
            if question_id < 0:
                return JsonResponse({'success':False})

            raw_answer = request.POST['answer']
            if int(raw_answer) > 0 and int(raw_answer) < 5:
                answer = int(raw_answer) 
            else:
                return JsonResponse({'success':False})

            user_purchase = UserPurchases.objects.filter(user_id = request.user.id).filter(product_id = "PROD-1").get(status=True)
            if(prev):
                if question_id == 0:
                    question_id += 1
                    answer = QuestionAnswer.objects.filter(purchase_id=user_purchase.id).filter(question_id=question_id).values()
                    question = Question.objects.filter(pk=question_id).values()
                    return JsonResponse({'success':True, 'final':False, 'question':list(question),'answer':list(answer)})
                question = Question.objects.filter(pk=question_id).values()    
                answer = QuestionAnswer.objects.filter(purchase_id=user_purchase.id).filter(question_id=question_id).values()
                return JsonResponse({'success':True, 'final':False, 'question':list(question),'answer':list(answer)})

            if question_id == 0:
                question_id += 1
                answer = QuestionAnswer.objects.filter(purchase_id=user_purchase.id).filter(question_id=question_id).values()
                question = Question.objects.filter(pk=question_id).values()
                return JsonResponse({'success':True, 'final':False, 'question':list(question),'answer':list(answer)})

            question = Question.objects.get(pk=question_id)
            count = QuestionAnswer.objects.filter(purchase_id = user_purchase.id).filter(question_id = question_id).count()
            if count > 0:
                QuestionAnswer.objects.filter(purchase_id = user_purchase.id).filter(question_id = question_id).update(answer = answer)
            else:
                QuestionAnswer.objects.create(
                    question=question,
                    purchase_id = user_purchase.id,
                    user = request.user,
                    answer = answer
                )
            if (submit):
                total_questions_answerd = QuestionAnswer.objects.filter(purchase_id = user_purchase.id).count()
                total_questions = Question.objects.count()
                if total_questions_answerd == total_questions:
                    print("All finished, calculating the result")
                    answers = QuestionAnswer.objects.filter(purchase_id = user_purchase.id)
                    p=0
                    i=0
                    c=0
                    s=0
                    e=0
                    t = 0
                    for answer in answers:
                        if (answer.question.category == "P"):
                            p += answer.answer
                        elif (answer.question.category == "I"):
                            i += answer.answer
                        elif (answer.question.category == "C"):  
                            c += answer.answer  
                        elif (answer.question.category == "S"):
                            s += answer.answer    
                        elif (answer.question.category == "E"):  
                            e += answer.answer  
                        else:  
                            t += answer.answer
                    Result.objects.create(
                        user = request.user,
                        pragmatic_score = p,
                        industrious_score = i,
                        creative_score = c,
                        socialite_score = s,
                        explorer_score = e,
                        traditional_score = t
                    )
                    UserPurchases.objects.filter(user_id = request.user.id).filter(product_id = "PROD-1").update(status=False)
                    return JsonResponse({'success':False,'redirect':True})    
            last_q = Question.objects.last()
            if question_id == last_q.id:
                return JsonResponse({'success':False,'redirect':True})
            elif question_id + 1 == last_q.id:   
                nextq = question_id + 1
                question = Question.objects.filter(pk=nextq).values()
                try:
                    answer = QuestionAnswer.objects.filter(purchase_id=user_purchase.id).filter(question_id=nextq).values()
                except: 
                    answer = None    
                return JsonResponse({'success':True, 'final':True, 'question':list(question),'answer':list(answer)})
            else:
                nextq = question_id + 1
                question = Question.objects.filter(pk=nextq).values() 
                try:
                    answer = QuestionAnswer.objects.filter(purchase_id=user_purchase.id).filter(question_id=nextq).values()
                    context = {'success':True, 'final':False, 'question':list(question),'answer':list(answer)}
                except:
                    answer = None  
                    context = {'success':True, 'final':False, 'question':list(question),'answer':answer}
  
                return JsonResponse(context)
        except Exception as e:
            return JsonResponse({'success':False})
    else:
        return JsonResponse({'success':False})

@login_required(login_url='login')
def getResult(request,id=None):
    try:
        if(id is None):
            result = Result.objects.filter(user_id = request.user.id).order_by('id').last()
        else:
            result = Result.objects.filter(user_id = request.user.id).get(pk=id)  
        total = 28
        p = int((int(result.pragmatic_score)/total)*100)
        i = int((int(result.industrious_score)/total)*100)
        c = int((int(result.creative_score)/total)*100)
        s = int((int(result.socialite_score)/total)*100)
        e = int((int(result.explorer_score)/total)*100)
        t = int((int(result.traditional_score)/total)*100)  
        percentage = {'P':p,'I':i,'C':c,'S':s,'E':e,'T':t} 
        k = Counter(percentage) 
        top = k.most_common(3)  
        context = {'result':result,'P':p,'I':i,'C':c,'S':s,'E':e,'T':t,'top':top}
        return render(request, 'picset/result.html',context)
    except Exception as e:
        print(e)
        return redirect('dashboard')    
    

@login_required(login_url='login')
def getPDF(request,id=None):
    try:
        if(id is None):
            result = Result.objects.filter(user_id = request.user.id).order_by('id').last()
        else:
            result = Result.objects.filter(user_id = request.user.id).get(pk=id)  
        total = 28
        p = int((int(result.pragmatic_score)/total)*100)
        i = int((int(result.industrious_score)/total)*100)
        c = int((int(result.creative_score)/total)*100)
        s = int((int(result.socialite_score)/total)*100)
        e = int((int(result.explorer_score)/total)*100)
        t = int((int(result.traditional_score)/total)*100)  
        percentage = {'P':p,'I':i,'C':c,'S':s,'E':e,'T':t} 
        k = Counter(percentage) 
        top = k.most_common(3)  
        context = {'result':result,'P':p,'I':i,'C':c,'S':s,'E':e,'T':t,'top':top}
        return render(request, 'picset/pdfview.html',context)
    except Exception as e:
        return redirect('dashboard')    
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

@login_required(login_url='login')
def downloadPDF(request,id=None):
    try:
        if(id is None):
            result = Result.objects.filter(user_id = request.user.id).order_by('id').last()
        else:
            result = Result.objects.filter(user_id = request.user.id).get(pk=id)  
        total = 28
        p = int((int(result.pragmatic_score)/total)*100)
        i = int((int(result.industrious_score)/total)*100)
        c = int((int(result.creative_score)/total)*100)
        s = int((int(result.socialite_score)/total)*100)
        e = int((int(result.explorer_score)/total)*100)
        t = int((int(result.traditional_score)/total)*100)  
        user = request.user
        percentage = {'P':p,'I':i,'C':c,'S':s,'E':e,'T':t} 
        k = Counter(percentage) 
        top = k.most_common(3)  
        context = {'result':result,'P':p,'I':i,'C':c,'S':s,'E':e,'T':t,'top':top,'user':user}
        # return render(request, 'picset/pdfview.html',context)
        pdf = render_to_pdf('picset/pdfview.html', context)
        return HttpResponse(pdf, content_type='application/pdf')
    except Exception as e:
        print(e)
        return redirect('dashboard')     