from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q
from django.http import Http404
from .models import Movie,Myrating,Category
from django.contrib import messages
from .forms import UserForm
from django.db.models import Case, When
from .recommendation import Myrecommend
import numpy as np 
import pandas as pd


# Öneriler
def recommend(request):
	if not request.user.is_authenticated:
		return redirect("login")
	if not request.user.is_active:
		raise Http404
	df=pd.DataFrame(list(Myrating.objects.all().values()))
	nu=df.user_id.unique().shape[0]
	current_user_id= request.user.id
 # Eğer yeni kullanıcı hiçbir filme puan vermediyse
	if current_user_id>nu:
		movie=Movie.objects.get(id=15)
		q=Myrating(user=request.user,movie=movie,rating=0)
		q.save()

	print("Current user id: ",current_user_id)
	prediction_matrix,Ymean = Myrecommend()
	my_predictions = prediction_matrix[:,current_user_id-1]+Ymean.flatten()
	pred_idxs_sorted = np.argsort(my_predictions)
	pred_idxs_sorted[:] = pred_idxs_sorted[::-1]
	pred_idxs_sorted=pred_idxs_sorted+1
	print(pred_idxs_sorted)
	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pred_idxs_sorted)])
	movie_list=list(Movie.objects.filter(id__in = pred_idxs_sorted,).order_by(preserved)[:10])
	return render(request,'web/recommend.html',{'movie_list':movie_list})


# Liste görünümü
def index(request):
	movies = Movie.objects.all()
	query  = request.GET.get('q')
	if query:
		movies = Movie.objects.filter(Q(title__icontains=query)).distinct()
		return render(request,'web/list.html',{'movies':movies})
	return render(request,'web/list.html',{'movies':movies})


# Detay görünümü
def detail(request,movie_id):
	if not request.user.is_authenticated:
		return redirect("login")
	if not request.user.is_active:
		raise Http404
	movies = get_object_or_404(Movie,id=movie_id)
	# Puanlama
	if request.method == "POST":
		rate = request.POST['rating']
		ratingObject = Myrating()
		ratingObject.user   = request.user
		ratingObject.movie  = movies
		ratingObject.rating = rate
		ratingObject.save()
		messages.success(request,"Değerlendirmeniz Kaydedildi")
		return redirect("index")
	return render(request,'web/detail.html',{'movies':movies})


# Kullanıcı kaydı
def signUp(request):
	form =UserForm(request.POST or None)
	if form.is_valid():
		user      = form.save(commit=False)
		username  =	form.cleaned_data['username']
		password  = form.cleaned_data['password']
		user.set_password(password)
		user.save()
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
	context ={
		'form':form
	}
	return render(request,'web/signUp.html',context)				


# Kullanıcı girişi
def Login(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
			else:
				return render(request,'web/login.html',{'error_message':'Hesabınız Devre Dışı Bırakıldı'})
		else:
			return render(request,'web/login.html',{'error_message': 'Hatalı Giriş'})
	return render(request,'web/login.html')

# Kullanıcı çıkışı
def Logout(request):
	logout(request)
	return redirect("login")

#Kategori
def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    movies = Movie.objects.filter(category=category)
    return render(request, 'web/list.html', {'movies': movies})

def categories(request):
    # Tüm türleri al
    genres = Movie.objects.values_list('genre', flat=True).distinct()
    return render(request, 'web/categories.html', {'genres': genres})