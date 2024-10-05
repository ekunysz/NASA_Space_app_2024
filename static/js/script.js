document
  .getElementById("dateForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    const fecha = document.getElementById("fecha").value;

    fetch("http://localhost:5000/api/planeta", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nombre: "Tierra",
        fecha: fecha,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Posición del planeta:", data);

        // Usa las coordenadas devueltas para renderizar en Three.js
        const x = data.x;
        const y = data.y;
        const z = data.z;

        // Configuración de la escena
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(
          75,
          window.innerWidth / window.innerHeight,
          0.1,
          1000
        );
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById("solarSystem").appendChild(renderer.domElement);

        // Crear el planeta (Tierra)
        const geometry = new THREE.SphereGeometry(0.5, 32, 32);
        const material = new THREE.MeshBasicMaterial({ color: 0x0000ff });
        const planet = new THREE.Mesh(geometry, material);
        scene.add(planet);

        planet.position.set(x, y, z);

        camera.position.z = 10;

        function animate() {
          requestAnimationFrame(animate);
          renderer.render(scene, camera);
        }

        animate();
      })
      .catch((error) => console.error("Error:", error));
  });
