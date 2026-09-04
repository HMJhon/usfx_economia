// Avatar 3D simple ("muñeco") construido con primitivas de Three.js.
// Editable en color mediante window.AVATAR_COLOR_PRIMARY / AVATAR_COLOR_SECONDARY.

(function () {
  const container = document.getElementById("avatar-container");
  if (!container || typeof THREE === "undefined") return;

  const width = container.clientWidth || 400;
  const height = container.clientHeight || 400;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
  camera.position.set(0, 1.4, 5);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  container.appendChild(renderer.domElement);

  // Luces
  scene.add(new THREE.AmbientLight(0xffffff, 0.7));
  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(3, 5, 4);
  scene.add(dirLight);

  const primaryColor = window.AVATAR_COLOR_PRIMARY || "#f4c542";
  const secondaryColor = window.AVATAR_COLOR_SECONDARY || "#2b6cb0";

  const bodyMat = new THREE.MeshStandardMaterial({ color: primaryColor });
  const limbMat = new THREE.MeshStandardMaterial({ color: secondaryColor });
  const headMat = new THREE.MeshStandardMaterial({ color: "#ffe0bd" });

  const avatar = new THREE.Group();

  // Cuerpo
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.6, 1.0, 8, 16), bodyMat);
  body.position.y = 1.1;
  avatar.add(body);

  // Cabeza
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.45, 24, 24), headMat);
  head.position.y = 2.1;
  avatar.add(head);

  // Ojos
  const eyeGeo = new THREE.SphereGeometry(0.05, 8, 8);
  const eyeMat = new THREE.MeshStandardMaterial({ color: "#222222" });
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(-0.15, 2.15, 0.4);
  const eyeR = eyeL.clone();
  eyeR.position.x = 0.15;
  avatar.add(eyeL, eyeR);

  // Sonrisa
  const smile = new THREE.Mesh(
    new THREE.TorusGeometry(0.15, 0.02, 8, 16, Math.PI),
    eyeMat
  );
  smile.position.set(0, 2.0, 0.4);
  smile.rotation.z = Math.PI;
  avatar.add(smile);

  // Brazo derecho (el que saluda)
  const armGeo = new THREE.CapsuleGeometry(0.12, 0.7, 6, 12);
  const armR = new THREE.Mesh(armGeo, limbMat);
  armR.position.set(0.75, 1.5, 0);
  armR.rotation.z = -0.6;
  avatar.add(armR);

  const armL = new THREE.Mesh(armGeo, limbMat);
  armL.position.set(-0.75, 1.1, 0);
  armL.rotation.z = 0.3;
  avatar.add(armL);

  // Piernas
  const legGeo = new THREE.CapsuleGeometry(0.15, 0.7, 6, 12);
  const legL = new THREE.Mesh(legGeo, limbMat);
  legL.position.set(-0.25, 0.1, 0);
  const legR = legL.clone();
  legR.position.x = 0.25;
  avatar.add(legL, legR);

  scene.add(avatar);
  avatar.position.y = -1.2;

  window.setAvatarColors = function (primary, secondary) {
    bodyMat.color.set(primary);
    limbMat.color.set(secondary);
  };

  // Animación: saludo del brazo, ligero rebote y rotación
  let t = 0;
  function animate() {
    requestAnimationFrame(animate);
    t += 0.05;
    armR.rotation.z = -0.6 + Math.sin(t * 3) * 0.5;
    avatar.position.y = -1.2 + Math.abs(Math.sin(t)) * 0.15;
    avatar.rotation.y = Math.sin(t * 0.5) * 0.3;
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", function () {
    const w = container.clientWidth || width;
    const h = container.clientHeight || height;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });

  // Globo de mensaje con efecto de escritura
  const bubble = document.getElementById("speech-bubble");
  if (bubble && window.AVATAR_MESSAGE) {
    let i = 0;
    const text = window.AVATAR_MESSAGE;
    const typing = setInterval(function () {
      bubble.textContent = text.slice(0, i);
      i++;
      if (i > text.length) clearInterval(typing);
    }, 30);
  }
})();
