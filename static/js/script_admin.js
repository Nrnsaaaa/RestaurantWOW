// Ambil elemen modal dan tombol Admin
var modal = document.getElementById("loginModal");
var adminLink = document.getElementById("adminLink");
var closeModal = document.getElementById("closeModal");

// Ketika klik Admin, buka modal
adminLink.onclick = function () {
  modal.style.display = "flex";
};

// Ketika klik tombol tutup, tutup modal
closeModal.onclick = function () {
  modal.style.display = "none";
};

// Ketika klik di luar modal, tutup modal
window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};
