<template>
    <div class="flex flex-col items-center gap-5 p-5 min-h-screen">
        <RouterLink
            to="/"
            class="fixed flex items-center top-5 left-5 gap-3 px-4 py-2 bg-white/80 rounded-full hover:scale-105 transition duration-300 ease-in-out hover:bg-white/90"
        >
            <img src="/chevron-left-solid.svg" alt="back" class="h-6" />
            <p>Retour</p>
        </RouterLink>
        <div class="w-full h-full p-5 mt-10 items-center flex flex-col gap-5">
            <img
                :src="asso?.logo"
                :alt="`logo_${name}`"
                class="h-36 rounded-full"
            />
            <h1 class="text-5xl text-white font-semibold py-10 text-center">
                {{ name }}
            </h1>
            <a
                :href="link"
                v-for="link in asso?.links"
                target="_blank"
                class="w-full max-w-3xl"
            >
                <ListItem
                    :key="link"
                    :title="determineLink(link)"
                    :logo="getLogoLink(link)"
                />
            </a>
        </div>
    </div>
</template>

<script setup lang="ts">
const route = useRoute();
const name = route.params.name;

import assos from "~/static/assos.json";

const asso = assos.find((asso) => asso.name === name);

const determineLink = (link: string) => {
    if (link.includes("discord")) {
        return "Discord";
    } else if (link.includes("t.me")) {
        return "Telegram";
    } else if (link.includes("facebook")) {
        return "Facebook";
    } else if (link.includes("instagram")) {
        return "Instagram";
    } else if (link.includes("youtube")) {
        return "Youtube";
    } else if (link.includes("tiktok")) {
        return "Tiktok";
    } else if (link.includes("snapchat")) {
        return "Snapchat";
    } else if (link.includes("linkedin")) {
        return "Linkedin";
    } else {
        return link;
    }
};

const getLogoLink = (link: string) => {
    if (link.includes("discord")) {
        return "/discord.svg";
    } else if (link.includes("t.me")) {
        return "/telegram.svg";
    } else if (link.includes("facebook")) {
        return "/facebook.svg";
    } else if (link.includes("instagram")) {
        return "/instagram.svg";
    } else if (link.includes("youtube")) {
        return "/youtube.svg";
    } else if (link.includes("tiktok")) {
        return "/tiktok.svg";
    } else if (link.includes("snapchat")) {
        return "/snapchat.svg";
    } else if (link.includes("linkedin")) {
        return "/linkedin.svg";
    } else {
        return "/laptop-solid.svg";
    }
};
</script>
