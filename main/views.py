from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import *
from .filters import PatientFilter
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# PatientFilter = OrderFilter

# Create your vie

def login(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('login')
        else:
            return render(request, 'main/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('/')




def dashboard(request):
    patients = Patient.objects.all()
    patient_count = patients.count()
    patients_recovered = Patient.objects.filter(status="Recuperado")
    patients_deceased = Patient.objects.filter(status="Fallecido")
    deceased_count = patients_deceased.count()
    recovered_count = patients_recovered.count()
    beds = Bed.objects.all()
    beds_available = Bed.objects.filter(occupied=False).count()
    context = {
        'patient_count': patient_count,
        'recovered_count': recovered_count,
        'beds_available': beds_available,
        'deceased_count':deceased_count,
        'beds':beds
    }
    print(patient_count)
    return render(request, 'main/dashboard.html', context)


def bed_list(request):
    beds = Bed.objects.all()
    context = {'beds':beds}
    return render(request, 'main/bed_list.html', context)   

def doctor_list(request):
    doctors = Doctor.objects.all()
    context = {'doctors':doctors}
    return render(request, 'main/doctor_list.html', context)

def enfm_list(request):
    enfermedads = Enfermedad.objects.all()
    context = {'enfermedads':enfermedads}
    return render(request, 'main/enfm_list.html', context)

def add_patient(request):
    beds = Bed.objects.filter(occupied=False)
    doctors = Doctor.objects.all()
    enfermedads=Enfermedad.objects.all()
    if request.method == "POST":
        dni = request.POST['dni']
        name = request.POST['name']
        phone_num = request.POST['phone_num']
        address = request.POST['address']
        bed_num_sent = request.POST['bed_num']
        bed_num = Bed.objects.get(bed_number=bed_num_sent)
        status = request.POST['status']
        doctor = request.POST['doctor']
        doctor = Doctor.objects.get(name=doctor)
        enfermedad = request.POST['enfermedad']
        enfermedad = Enfermedad.objects.get(name=enfermedad)
        patient = Patient.objects.create(
        dni=dni,   
        name = name,
        phone_num = phone_num, 
        address = address, 
        bed_num = bed_num,
        doctor=doctor,
        status = status,
        enfermedad=enfermedad
        )
        patient.save()

        bed = Bed.objects.get(bed_number=bed_num_sent)
        bed.occupied = True
        bed.save()
        id = patient.id
        return redirect(f"/patient/{id}")
        
    context = {
        'beds': beds,
        'doctors': doctors,
        'enfermedads':enfermedads
    }
    return render(request, 'main/add_patient.html', context)


def delete_patient(request,pk):
    patient = Patient.objects.get(id=pk)
    bed = Bed.objects.get(bed_number=patient.bed_num)
    if request.method == "POST":
        bed.occupied = False
        bed.save()
        patient.delete() 
        return redirect("patient_list")
        
    context = {
        'patient': patient,
        'bed':bed
    }
    return render(request, 'main/delete_patient.html', context)

def patient(request, pk):
    patient = Patient.objects.get(id=pk)
    
    if request.method == "POST":
        name = request.POST['name']
        phone_num = request.POST['phone_num']
        address  = request.POST['location']
        status = request.POST['status']
        doctor_notes = request.POST['doctor_notes']
        '''
        doctor = request.POST['doctor']
        doctor = Doctor.objects.get(name=doctor)
        enfermedad = request.POST['enfermedad']
        enfermedad = Enfermedad.objects.get(name=enfermedad)

        patient.doctor = doctor
        patient.enfermedad=enfermedad
        '''  
        patient.name=name
        patient.phone_num = phone_num
        patient.address = address
        patient.doctors_notes = doctor_notes
        print(patient.doctors_notes)
        patient.status = status
        patient.save()
        
        return redirect("patient_list")
    context = {
        'patient': patient,
     }
    return render(request, 'main/patient.html', context)


def patient_list(request):
    patients = Patient.objects.all()

    # filtering
    myFilter = PatientFilter(request.GET, queryset=patients)

    patients = myFilter.qs
    context = {
        'patients': patients,
        'myFilter': myFilter
    }

    return render(request, 'main/patient_list.html', context)
    
'''
def consulta(request):
    patients = Patient.objects.all()

    # filtering
    myFilter = PatientFilter(request.GET, queryset=patients)

    patients = myFilter.qs
    context = {
        'patients': patients,
        'myFilter': myFilter
    }

    return render(request, 'main/consulta.html', context)

def autocomplete(request):
    if patient in request.GET:
        name = Patient.objects.filter(name__icontains=request.GET.get(patient))
        name = ['js', 'python']
        
        names = list()
        names.append('Shyren')
        print(names)
        for patient_name in name:
            names.append(patient_name.name)
        return JsonResponse(names, safe=False)
    return render (request, 'main/patient_list.html')
'''

def autosuggest(request):
    query_original = request.GET.get('term')
    queryset = Patient.objects.filter(name__icontains=query_original)
    mylist = []
    mylist += [x.name for x in queryset]
    return JsonResponse(mylist, safe=False)

def autodoctor(request):
    query_original = request.GET.get('term')
    queryset = Doctor.objects.filter(name__icontains=query_original)
    mylist = []
    mylist += [x.name for x in queryset]
    return JsonResponse(mylist, safe=False)

