<script setup>
import AccordionTest from './accordioncomps/AccordionTest.vue';
import CustomerAccordion from './accordioncomps/CustomerAccordion.vue';
import SupplierAccordion from './accordioncomps/SupplierAccordion.vue';
import SidebarTwo from './SidebarTwo.vue';

const call ='SupplierAccordion'

</script>

<template>

  <div class="sm:mx-10 sm:w-1/4">

    <AccordionTest>
      <SupplierAccordion/>
    </AccordionTest>
  </div>


</template>
