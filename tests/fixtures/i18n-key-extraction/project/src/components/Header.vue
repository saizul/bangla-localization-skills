<template>
  <header>
    <a href="/" title="Go to homepage">{{ $t('nav.home') }}</a>
    <span>{{ $t('nav.cart', { count: items }) }}</span>
    <button @click="logout">Sign out</button>
  </header>
</template>

<script>
export default {
  data() {
    return { mode: "dark", label: this.$t("nav.menu") };
  },
};
</script>
