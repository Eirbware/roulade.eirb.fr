<template>
    <div
        class="flex items-center justify-center rounded-md w-full gap-5 drop-shadow-md backdrop-blur-md bg-white/80 box-border h-24 overflow-hidden hover:bg-white/95 hover:scale-105 transition duration-300 ease-in-out"
    >
        <img
            :src="logo"
            :alt="`logo_${title}`"
            class="h-24 absolute left-0 scale-105"
        />
        <h1
            class="font-semibold text-2xl pl-28 pr-5 md:pr-28 overflow-clip text-ellipsis"
        >
            {{ title }}
        </h1>
    </div>
</template>

<script setup lang="ts">
defineProps({
    title: {
        type: String,
        required: true,
    },
    // color: {
    //     type: String,
    //     required: true,
    // },
    logo: {
        type: String,
        required: true,
    },
});
</script>
