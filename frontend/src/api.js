
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export function token(){ return localStorage.getItem("gymflow_token"); }
export function user(){ try{return JSON.parse(localStorage.getItem("gymflow_user")||"null")}catch{return null} }
export function setSession(data){ localStorage.setItem("gymflow_token",data.access_token); localStorage.setItem("gymflow_user",JSON.stringify(data.user)); }
export function clearSession(){ localStorage.removeItem("gymflow_token"); localStorage.removeItem("gymflow_user"); }
async function request(path,{method="GET",body,auth=true}={}){
  const headers={"Content-Type":"application/json"};
  if(auth && token()) headers.Authorization=`Bearer ${token()}`;
  const res=await fetch(`${API_URL}${path}`,{method,headers,body:body===undefined?undefined:JSON.stringify(body)});
  let data=null; try{data=await res.json()}catch{}
  if(!res.ok){ const msg=data?.detail || data?.message || `Request failed (${res.status})`; throw new Error(typeof msg==="string"?msg:JSON.stringify(msg));}
  return data;
}
export const api={
  health:()=>request("/health",{auth:false}),
  login:(body)=>request("/api/v1/auth/login",{method:"POST",body,auth:false}),
  verifyActivation:(body)=>request("/api/v1/auth/verify-activation",{method:"POST",body,auth:false}),
  setupPassword:(body)=>request("/api/v1/auth/setup-password",{method:"POST",body,auth:false}),
  me:()=>request("/api/v1/auth/me"),
  logout:()=>request("/api/v1/auth/logout",{method:"POST"}),
  saasDashboard:()=>request("/api/v1/saas/dashboard"),
  gyms:()=>request("/api/v1/saas/gyms"),
  gym:(id)=>request(`/api/v1/saas/gyms/${id}`),
  createGym:(body)=>request("/api/v1/saas/gyms",{method:"POST",body}),
  updateGymSaas:(id,body)=>request(`/api/v1/saas/gyms/${id}`,{method:"PATCH",body}),
  disableGym:(id)=>request(`/api/v1/saas/gyms/${id}`,{method:"DELETE"}),
  saasPlans:()=>request("/api/v1/saas/plans"),
  createSaasPlan:(body)=>request("/api/v1/saas/plans",{method:"POST",body}),
  updateSaasPlan:(id,body)=>request(`/api/v1/saas/plans/${id}`,{method:"PATCH",body}),
  gymSubs:()=>request("/api/v1/saas/gym-subscriptions"),
  createGymSub:(body)=>request("/api/v1/saas/gym-subscriptions",{method:"POST",body}),
  updateGymSub:(id,body)=>request(`/api/v1/saas/gym-subscriptions/${id}`,{method:"PATCH",body}),
  gymDashboard:()=>request("/api/v1/gym/dashboard"),
  getGym:()=>request("/api/v1/gym"),
  updateGym:(body)=>request("/api/v1/gym",{method:"PATCH",body}),
  staffDashboard:()=>request("/api/v1/staff/dashboard"),
  staff:()=>request("/api/v1/staff"),
  createStaff:(body)=>request("/api/v1/staff",{method:"POST",body}),
  updateStaff:(id,body)=>request(`/api/v1/staff/${id}`,{method:"PATCH",body}),
  disableStaff:(id)=>request(`/api/v1/staff/${id}`,{method:"DELETE"}),
  members:()=>request("/api/v1/members"),
  member:(id)=>request(`/api/v1/members/${id}`),
  createMember:(body)=>request("/api/v1/members",{method:"POST",body}),
  updateMember:(id,body)=>request(`/api/v1/members/${id}`,{method:"PATCH",body}),
  deleteMember:(id)=>request(`/api/v1/members/${id}`,{method:"DELETE"}),
  plans:()=>request("/api/v1/plans"),
  createPlan:(body)=>request("/api/v1/plans",{method:"POST",body}),
  updatePlan:(id,body)=>request(`/api/v1/plans/${id}`,{method:"PATCH",body}),
  deletePlan:(id)=>request(`/api/v1/plans/${id}`,{method:"DELETE"}),
  subscriptions:()=>request("/api/v1/subscriptions"),
  createSubscription:(body)=>request("/api/v1/subscriptions",{method:"POST",body}),
  updateSubscription:(id,body)=>request(`/api/v1/subscriptions/${id}`,{method:"PATCH",body}),
  payments:()=>request("/api/v1/payments"),
  createPayment:(body)=>request("/api/v1/payments",{method:"POST",body}),
  attendance:()=>request("/api/v1/attendance"),
  checkIn:(member_id)=>request("/api/v1/attendance/check-in",{method:"POST",body:{member_id}}),
  checkOut:(id)=>request(`/api/v1/attendance/${id}/check-out`,{method:"POST"}),
  measurements:(memberId)=>request(`/api/v1/members/${memberId}/measurements`),
  createMeasurement:(memberId,body)=>request(`/api/v1/members/${memberId}/measurements`,{method:"POST",body}),
  updateMeasurement:(memberId,id,body)=>request(`/api/v1/members/${memberId}/measurements/${id}`,{method:"PATCH",body}),
};
export {API_URL};
