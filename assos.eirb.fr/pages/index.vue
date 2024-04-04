<template>
    <div class="flex flex-col items-center gap-5 p-5 min-h-screen">
        <h1
            class="md:text-5xl text-3xl text-white font-semibold py-10 text-center"
        >
            Clubs et Assosciations de <br />
            <span class="font-bold text-yellow-500">l'ENSEIRB-MATMECA</span>
        </h1>

        <input
            type="text"
            name="filter"
            id="filter"
            v-model="filter"
            placeholder="Rechercher un club ou une association"
            class="w-full max-w-3xl border-b-2 border-white/50 bg-transparent text-white text-2xl font-semibold placeholder-white/50 placeholder-opacity-50 focus:outline-none focus:border-white/80 transition duration-300 ease-in-out"
        />

        <RouterLink
            :to="`/${asso.name}`"
            class="w-full max-w-3xl"
            v-for="asso in filteredAssos"
        >
            <ListItem
                :key="asso.name"
                :title="asso.name"
                :links="asso.links"
                :logo="asso.logo"
            />
        </RouterLink>
    </div>
</template>

<script setup lang="ts">
import ListItem from "../components/ListItem.vue";
import assos from "../static/assos.json";

const filter = ref("");

const filteredAssos = computed(() => {
    return assos
        .filter((asso) =>
            asso.name.toLowerCase().includes(filter.value.toLowerCase())
        )
        .sort((a, b) => {
            if (a.name < b.name) {
                return -1;
            } else if (a.name > b.name) {
                return 1;
            } else {
                return 0;
            }
        });
});
</script>
