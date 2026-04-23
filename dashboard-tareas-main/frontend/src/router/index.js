import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/loginView.vue";
import RegisterView from "../views/registerView.vue";
import MainLayout from "../layouts/MainLayout.vue";
import TableroView from "../views/TableroView.vue";
import AuditoriaView from "../views/AuditoriaView.vue";
import EquipoView from "../views/EquipoView.vue";
import ReportesView from "../views/ReportesView.vue";
import { useAuth } from "../composables/useAuth.js";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/dashboard" },
    { path: "/login", name: "login", component: LoginView },
    { path: "/register", name: "register", component: RegisterView },
    { 
      path: "/dashboard", 
      component: MainLayout, 
      meta: { requiresAuth: true },
      children: [
        { path: "", name: "dashboard", component: TableroView },
        { path: "audit", name: "audit", component: AuditoriaView },
        { path: "equipo", name: "equipo", component: EquipoView },
        { path: "reportes", name: "reportes", component: ReportesView }
      ]
    },
  ],
});

router.beforeEach(async (to) => {
  const { isAuthenticated, user, fetchMe } = useAuth();

  if (to.meta.requiresAuth) {
    if (!isAuthenticated.value) return { name: "login" };

    if (!user.value) {
      await fetchMe();
      if (!user.value) return { name: "login" };
    }
  }

  if (to.name === "login" && isAuthenticated.value) {
    if (!user.value) await fetchMe();
    if (user.value) return { name: "dashboard" };
  }

  return true;
});

export default router;
