document.addEventListener("DOMContentLoaded", function () {
  const paymentModal = document.getElementById("paymentModal");
  const bayarButton = document.getElementById("bayarButton");
  const closeModalButton = document.getElementById("closePaymentModal"); // Ganti ID
  const payCOD = document.getElementById("payCOD");
  const payWA = document.getElementById("payWA");

  function showPaymentOptions() {
    paymentModal.style.display = "flex";
  }

  function closeModal() {
    paymentModal.style.display = "none";
  }

  function bayarDiTempat() {
    alert("Anda memilih 'Bayar di Tempat'. Silakan siapkan uang tunai.");
    closeModal();
  }

  function hubungiWhatsApp() {
    window.location.href =
      "https://wa.me/082118757945?text=Halo,%20saya%20ingin%20melakukan%20pembayaran%20pesanan.";
  }

  // Sembunyikan modal di awal
  paymentModal.style.display = "none";

  // Event listener hanya aktif saat tombol diklik
  if (bayarButton) bayarButton.addEventListener("click", showPaymentOptions);
  if (closeModalButton) closeModalButton.addEventListener("click", closeModal); // Pastikan ID yang benar
  if (payCOD) payCOD.addEventListener("click", bayarDiTempat);
  if (payWA) payWA.addEventListener("click", hubungiWhatsApp);
});
