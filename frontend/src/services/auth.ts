import api from "./api";

export const authService = {
  async register(email: string, password: string) {
    const response = await api.post("/auth/register", { email, password });
    return response.data;
  },

  async login(email: string, password: string) {
    // Standard OAuth2 form-urlencoded parameters
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);

    const response = await api.post("/auth/login", params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    
    // Save token to localStorage
    if (response.data.access_token) {
      localStorage.setItem("veritas_token", response.data.access_token);
    }
    return response.data;
  },

  async getMe() {
    const response = await api.get("/auth/me");
    return response.data;
  },

  logout() {
    localStorage.removeItem("veritas_token");
  }
};
