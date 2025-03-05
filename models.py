from django.db import models
from django.contrib.auth.models import User

class PengajuanKredit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    konsumen = models.ForeignKey(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)
    nik = models.CharField(max_length=16, unique=True)
    tanggal_lahir = models.DateField()
    status_perkawinan = models.CharField(max_length=50)
    data_pasangan = models.TextField(blank=True, null=True)
    dealer = models.CharField(max_length=255)
    model_kendaraan = models.CharField(max_length=255)
    tipe_kendaraan = models.CharField(max_length=255)
    warna_kendaraan = models.CharField(max_length=255)
    harga_kendaraan = models.DecimalField(max_digits=15, decimal_places=2)
    asuransi = models.BooleanField(default=True)
    down_payment = models.DecimalField(max_digits=15, decimal_places=2)
    lama_kredit = models.IntegerField(help_text='Dalam bulan')
    angsuran_per_bulan = models.DecimalField(max_digits=15, decimal_places=2)
    dokumen_ktp = models.FileField(upload_to='dokumen/ktp/')
    dokumen_spk = models.FileField(upload_to='dokumen/spk/')
    dokumen_pembayaran = models.FileField(upload_to='dokumen/bukti_pembayaran/')
    dokumen_ttd = models.FileField(upload_to='dokumen/ttd/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nama} - {self.model_kendaraan}"

# Membuat Form untuk Input Pengajuan Kredit
from django import forms

class PengajuanKreditForm(forms.ModelForm):
    class Meta:
        model = PengajuanKredit
        fields = ['nama', 'nik', 'tanggal_lahir', 'status_perkawinan', 'data_pasangan', 'dealer', 'model_kendaraan', 
                  'tipe_kendaraan', 'warna_kendaraan', 'harga_kendaraan', 'asuransi', 'down_payment', 'lama_kredit', 
                  'angsuran_per_bulan', 'dokumen_ktp', 'dokumen_spk', 'dokumen_pembayaran']

class TandaTanganForm(forms.ModelForm):
    class Meta:
        model = PengajuanKredit
        fields = ['dokumen_ttd']

# Membuat Views untuk Menampilkan Form dan Menyimpan Data
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def ajukan_kredit(request):
    if request.method == 'POST':
        form = PengajuanKreditForm(request.POST, request.FILES)
        if form.is_valid():
            pengajuan = form.save(commit=False)
            pengajuan.konsumen = request.user
            pengajuan.save()
            messages.success(request, "Pengajuan kredit berhasil diajukan.")
            return redirect('dashboard')
    else:
        form = PengajuanKreditForm()
    return render(request, 'pengajuan_form.html', {'form': form})

# Membuat Views untuk Approval Atasan Marketing
@login_required
def approval_pengajuan(request, pengajuan_id):
    pengajuan = get_object_or_404(PengajuanKredit, id=pengajuan_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['approved', 'rejected']:
            pengajuan.status = status
            pengajuan.save()
            messages.success(request, f"Pengajuan kredit {status}.")
        return redirect('dashboard')
    return render(request, 'approval_form.html', {'pengajuan': pengajuan})

# Membuat View untuk Upload Dokumen Tanda Tangan Digital
@login_required
def upload_dokumen_ttd(request, pengajuan_id):
    pengajuan = get_object_or_404(PengajuanKredit, id=pengajuan_id)
    if request.method == 'POST':
        form = TandaTanganForm(request.POST, request.FILES, instance=pengajuan)
        if form.is_valid():
            form.save()
            messages.success(request, "Dokumen tanda tangan berhasil diunggah.")
            return redirect('dashboard')
    else:
        form = TandaTanganForm()
    return render(request, 'upload_ttd.html', {'form': form, 'pengajuan': pengajuan})

# Menyiapkan URL Routing
from django.urls import path
from . import views

urlpatterns = [
    path('ajukan-kredit/', views.ajukan_kredit, name='ajukan_kredit'),
    path('approval/<int:pengajuan_id>/', views.approval_pengajuan, name='approval_pengajuan'),
    path('upload-ttd/<int:pengajuan_id>/', views.upload_dokumen_ttd, name='upload_dokumen_ttd'),
]

# Template HTML
TEMPLATE_PENGAJUAN = """
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Ajukan Kredit</button>
</form>
"""

TEMPLATE_APPROVAL = """
<form method="post">
    {% csrf_token %}
    <label>Status:</label>
    <select name="status">
        <option value="approved">Approve</option>
        <option value="rejected">Reject</option>
    </select>
    <button type="submit">Submit</button>
</form>
"""

TEMPLATE_UPLOAD_TTD = """
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Upload Tanda Tangan</button>
</form>
"""