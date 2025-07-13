<template>
  <div class="about-page">
    <section class="hero">
      <h1>About This App</h1>
      <p class="subtitle">
        A modern asset management system for departments and categories—built with Django & Vue.
      </p>
    </section>

    <section class="content">
      <h2 class="ali-signature">
        <span class="icon">🚀</span>
        Developed By Ali Ghaderi Pour
      </h2>
      <div class="tech-tags">
        <span>Vue 3</span>
        <span>Pinia</span>
        <span>Pinia PersistedState</span>
        <span>Vue Router</span>
        <span>Django</span>
        <span>Django REST Framework</span>
        <span>SQL Server</span>
        <span>Jalali Calendar</span>
        <span>RTL Layout</span>
        <span>ESLint & Prettier</span>
        <span>File Upload</span>
      </div>
    </section>
  </div>
</template>

<script setup>
// static page, no logic needed!
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@700;900&display=swap');

.about-page {
  max-width: 900px;
  margin: 2.5rem auto;
  padding: 2.8rem 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ef 100%);
  border-radius: 22px;
  box-shadow: 0 8px 32px 0 rgba(57, 88, 131, 0.12);
  border: 1.5px solid #e8eaee;
  font-family: 'Vazirmatn', Vazir, Tahoma, Arial, sans-serif;
  direction: ltr !important;
  transition: box-shadow .25s;
}

.about-page:hover {
  box-shadow: 0 14px 36px 0 rgba(57, 88, 131, 0.15);
}

.hero {
  text-align: center;
  margin-bottom: 2rem;
}

.hero h1 {
  font-size: 2.3rem;
  font-weight: 900;
  letter-spacing: -.5px;
  background: linear-gradient(95deg, #6366F1 40%, #06b6d4 80%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.16rem;
  color: #475569;
  margin-bottom: .1rem;
  font-weight: 500;
}

.content h2.ali-signature {
  font-size: 1.6rem;
  margin-top: 2.1rem;
  margin-bottom: 0.8rem;
  font-weight: 900;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(92deg, #14b8a6 5%, #6366f1 80%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: text-shadow 0.2s;
  text-shadow: 0 2px 12px #b3bcf533;
  position: relative;
  overflow: visible;
}

.ali-signature .icon {
  font-size: 1.4em;
  animation: rocketFly 1.7s cubic-bezier(.7,-0.1,.84,.27) infinite alternate;
}
@keyframes rocketFly {
  0%   { transform: translateY(0);}
  87%  { transform: translateY(-10px) scale(1.18);}
  100% { transform: translateY(0) scale(1);}
}

.content p {
  font-size: 1.04rem;
  line-height: 1.72;
  color: #4b5563;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: .7rem;
  margin-top: 1.2rem;
  justify-content: start;
}

.tech-tags span {
  background: linear-gradient(92deg, #e0e7ef 5%, #f0fdfa 40%, #f1f5f9 100%);
  color: #334155;
  box-shadow: 0 1.5px 8px #6366f104;
  border-radius: 10px;
  font-size: .92rem;
  font-weight: 700;
  letter-spacing: .2px;
  padding: 0.37rem 1.05rem;
  border: 1px solid #d0d7e6;
  transition: background .12s, box-shadow .16s, color .15s;
  cursor: pointer;
}

.tech-tags span:hover {
  background: linear-gradient(87deg, #bae6fd 25%, #a7f3d0 50%, #e0e7ef 100%);
  color: #155e75;
  box-shadow: 0 8px 32px 0 rgba(56, 193, 235, 0.12);
  border-color: #6ee7b7;
}

@media (max-width: 600px) {
  .about-page { padding: 1.2rem .3rem; }
  .tech-tags span { font-size: .77rem; }
  .hero h1 { font-size: 1.42rem; }
  .content h2.ali-signature { font-size: 1.08rem; }
}
</style>
