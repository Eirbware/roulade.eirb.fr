<template>
    <div class="bg fixed h-screen w-screen -z-10"></div>
    <NuxtPage />
</template>

<style>
* {
    font-family: "Outfit", sans-serif;
}

body {
    background: #101523;
}

.bg {
    background: url("/fond.png");
    background-size: cover;
    background-position: center;
}

.scale-enter-active,
.scale-leave-active {
    transition: all 300ms ease;
}

.scale-enter-from,
.scale-leave-to {
    opacity: 0;
}

::-webkit-scrollbar {
    width: 20px;
    position: absolute;
}

::-webkit-scrollbar-track {
    background-color: transparent;
    backdrop-filter: blur(12px);
}

::-webkit-scrollbar-thumb {
    background-color: #c7c8d1cc;
    backdrop-filter: blur(12px);
}

::-webkit-scrollbar-thumb {
    background-color: #c7c8d1cc;
    backdrop-filter: blur(12px);
    border-radius: 20px;
}

::-webkit-scrollbar-thumb {
    background-color: #c7c8d1cc;
    backdrop-filter: blur(12px);
    border-radius: 20px;
    border: 6px solid transparent;
    background-clip: content-box;
}

::-webkit-scrollbar-thumb:hover {
    background-color: white;
}
</style>
