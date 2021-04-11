<template>
  <user-detail :is-edit="true" />
</template>

<script>
import UserDetail from './UserDetail'

export default {
  name: 'EditForm',
  components: { UserDetail }
}
</script>
