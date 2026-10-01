(() => {
  const canvas = document.querySelector('.loop-art');
  const context = canvas.getContext('2d');
  if (!context) return;

  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const hero = canvas.parentElement;
  const TAU = Math.PI * 2;
  let width = 0;
  let height = 0;
  let frame = 0;
  let elapsed = 0;
  let previous = 0;
  let visible = true;

  function project(u, v, time) {
    const radius = Math.min(width * 0.37, height * 0.52, 340);
    const tube = radius * 0.22;
    const turn = time * 0.065;
    const tilt = 0.83 + Math.sin(time * 0.09) * 0.12;
    const x = (radius + tube * Math.cos(v)) * Math.cos(u);
    const y = (radius + tube * Math.cos(v)) * Math.sin(u);
    const z = tube * Math.sin(v);
    const ry = y * Math.cos(tilt) - z * Math.sin(tilt);
    const rz = y * Math.sin(tilt) + z * Math.cos(tilt);
    const rx = x * Math.cos(turn) + rz * Math.sin(turn);
    const depth = -x * Math.sin(turn) + rz * Math.cos(turn);
    const perspective = 1400 / (1400 + depth);
    return {
      x: width / 2 + (rx * 0.98 - ry * 0.19) * perspective,
      y: height / 2 + (rx * 0.19 + ry * 0.98) * perspective,
      depth: depth / radius,
    };
  }

  function draw(time) {
    context.clearRect(0, 0, width, height);
    context.lineWidth = 0.65;
    // A closed wire loop, with no external graphics dependencies.
    for (let ring = 0; ring < 12; ring++) {
      context.beginPath();
      for (let step = 0; step <= 96; step++) {
        const p = project(step / 96 * TAU, ring / 12 * TAU, time);
        if (step === 0) context.moveTo(p.x, p.y);
        else context.lineTo(p.x, p.y);
      }
      context.strokeStyle = 'rgba(90, 114, 153, 0.14)';
      context.stroke();
    }
    for (let segment = 0; segment < 48; segment++) {
      context.beginPath();
      for (let step = 0; step <= 24; step++) {
        const p = project(segment / 48 * TAU, step / 24 * TAU, time);
        if (step === 0) context.moveTo(p.x, p.y);
        else context.lineTo(p.x, p.y);
      }
      context.strokeStyle = 'rgba(90, 114, 153, 0.1)';
      context.stroke();
    }
    for (let dot = 0; dot < 4; dot++) {
      const p = project(time * 0.12 + dot * TAU / 4, dot * 1.7, time);
      context.beginPath();
      context.arc(p.x, p.y, 2.3, 0, TAU);
      context.fillStyle = `rgba(57, 112, 207, ${0.35 - p.depth * 0.12})`;
      context.fill();
    }
  }

  function tick(now) {
    frame = requestAnimationFrame(tick);
    if (now - previous < 1000 / 30) return;
    if (previous) elapsed += Math.min(now - previous, 100) / 1000;
    previous = now;
    draw(elapsed);
  }

  function updateMotion() {
    cancelAnimationFrame(frame);
    previous = 0;
    draw(elapsed);
    if (!motion.matches && !document.hidden && visible) {
      frame = requestAnimationFrame(tick);
    }
  }

  new ResizeObserver(() => {
    width = hero.clientWidth;
    height = hero.clientHeight;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    updateMotion();
  }).observe(hero);

  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    updateMotion();
  }).observe(hero);

  motion.addEventListener('change', updateMotion);
  document.addEventListener('visibilitychange', updateMotion);
})();
