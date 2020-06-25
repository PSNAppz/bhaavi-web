from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from accounts.models import *
from django.http import JsonResponse
from django.contrib import messages

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
                   

            if count > 0:
                QuestionAnswer.objects.filter(purchase_id = user_purchase.id).filter(question_id = question_id).update(answer = answer)
            else:
                QuestionAnswer.objects.create(
                    question=question,
                    purchase_id = user_purchase.id,
                    user = request.user,
                    answer = answer
                )
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
            result = Result.objects.get(pk=id)  
        print(result.pragmatic_score)
        
    except Exception as e:
        print(e)
        return redirect('dashboard')    
    