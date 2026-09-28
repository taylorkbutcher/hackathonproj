document.getElementById('helloBtn').addEventListener('click', () => {
  document.getElementById('message').textContent = 'Hello! Thanks for visiting.';
});

document.getElementById('contactForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const name = document.getElementById('name').value;
  document.getElementById('formMsg').textContent = `Thanks, ${name}! I'll get back to you soon.`;
  e.target.reset();
});
