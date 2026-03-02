(function () {
  var openBtn = document.getElementById("openCamera");
  var cameraModal = document.getElementById("cameraModal");
  var cropModal = document.getElementById("cropModal");
  var closeCamera = document.getElementById("closeCamera");
  var closeCrop = document.getElementById("closeCrop");
  var startBtn = document.getElementById("startCamera");
  var captureBtn = document.getElementById("captureFrame");
  var saveBtn = document.getElementById("saveAvatar");
  var video = document.getElementById("cameraStream");
  var canvas = document.getElementById("captureCanvas");
  var previewImg = document.getElementById("cropPreview");
  var form = document.getElementById("avatarForm");
  var stream = null;
  var cropper = null;

  function openCamera() {
    cameraModal.classList.remove("hidden");
  }

  function closeCameraModal() {
    cameraModal.classList.add("hidden");
    if (stream) {
      stream.getTracks().forEach(function (track) { track.stop(); });
      stream = null;
    }
  }

  function openCrop() {
    cropModal.classList.remove("hidden");
  }

  function closeCropModal() {
    cropModal.classList.add("hidden");
    if (cropper) {
      cropper.destroy();
      cropper = null;
    }
  }

  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      video.srcObject = stream;
      await video.play();
    } catch (err) {
      alert("Kamera tidak bisa diakses.");
    }
  }

  function capture() {
    if (!video.videoWidth) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    var ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    previewImg.onload = function () {
      if (cropper) cropper.destroy();
      cropper = new Cropper(previewImg, {
        aspectRatio: 1,
        viewMode: 1,
        dragMode: "move",
        background: false,
        guides: false,
        autoCropArea: 0.9,
      });
    };
    previewImg.src = canvas.toDataURL("image/png");
    closeCameraModal();
    openCrop();
  }

  function save() {
    if (!cropper) return;
    var croppedCanvas = cropper.getCroppedCanvas({
      width: 320,
      height: 320,
      imageSmoothingQuality: "high",
    });
    var output = document.createElement("canvas");
    output.width = 320;
    output.height = 320;
    var ctx = output.getContext("2d");
    ctx.save();
    ctx.beginPath();
    ctx.arc(160, 160, 160, 0, Math.PI * 2);
    ctx.closePath();
    ctx.clip();
    ctx.drawImage(croppedCanvas, 0, 0, 320, 320);
    ctx.restore();

    output.toBlob(function (blob) {
      var formData = new FormData();
      formData.append("photo", blob, "avatar.png");
      fetch(form.action, { method: "POST", body: formData })
        .then(function () { window.location.reload(); });
    }, "image/png");
  }

  if (openBtn) openBtn.addEventListener("click", openCamera);
  if (closeCamera) closeCamera.addEventListener("click", closeCameraModal);
  if (closeCrop) closeCrop.addEventListener("click", closeCropModal);
  if (startBtn) startBtn.addEventListener("click", startCamera);
  if (captureBtn) captureBtn.addEventListener("click", capture);
  if (saveBtn) saveBtn.addEventListener("click", save);
})();
