
import React,{useEffect,useMemo,useState} from "react";
import {createRoot} from "react-dom/client";
import {api,setSession,clearSession,user,token} from "./api";
import "./styles.css";

const fmt=(d)=>d?new Date(d).toLocaleDateString():"—";
const shortId=(v)=>v?String(v).slice(0,8):"—";
const isoDate=(d)=>{const x=new Date(d);return Number.isNaN(x.getTime())?"":x.toISOString().slice(0,10)};
const addMonths=(date,months)=>{const d=new Date(`${date}T00:00:00`);if(Number.isNaN(d.getTime()))return "";const day=d.getDate();d.setDate(1);d.setMonth(d.getMonth()+Number(months||0));const last=new Date(d.getFullYear(),d.getMonth()+1,0).getDate();d.setDate(Math.min(day,last));return isoDate(d)};
const downloadFile=(name,text,type="application/json")=>{const blob=new Blob([text],{type});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;a.click();URL.revokeObjectURL(a.href)};
const money=(n)=>`$${Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}`;
function errText(e){return e?.message||"Something went wrong";}
function Modal({title,onClose,children,wide=false}){return <div className="overlay"><div className={"modal "+(wide?"wide":"")}><div className="modal-head"><h2>{title}</h2><button className="icon-btn" onClick={onClose}>×</button></div>{children}</div></div>}
function Toast({msg,type="ok"}){return msg?<div className={"toast "+type}>{msg}</div>:null}

function Shell({children,role,onNavigate,page,onLogout}){
 const [lang,setLang]=useState("English"); const [status,setStatus]=useState(null);
 const saas=role==="saas_admin", staff=role==="staff";
 const nav=saas?[
  ["dashboard","Dashboard","▦"],["gyms","Gyms","▣"],["saas-plans","SaaS Plans","◆"],["gym-subs","Gym Subscriptions","◈"],["settings","Settings","⚙"]
 ]:staff?[
  ["dashboard","Dashboard","▦"],["members","Members","●"],["subscriptions","Subscriptions","◈"],["payments","Payments","$"],["attendance","Attendance","✓"],["measurements","Measurements","◉"]
 ]:[
  ["dashboard","Dashboard","▦"],["staff","Staff","♙"],["members","Members","●"],["plans","Plans","◆"],["subscriptions","Subscriptions","◈"],["payments","Payments","$"],["attendance","Attendance","✓"],["measurements","Measurements","◉"],["settings","Gym Settings","⚙"]
 ];
 const u=user();
 const check=async()=>{try{await api.health();setStatus("Online")}catch{setStatus("Offline")}};
 return <div className="app"><aside className="sidebar">
   <div className="brand"><span className="logo">G</span><div><b>GymFlow Pro</b><small>{saas?"SaaS Administrator":staff?"Staff":"Gym Administrator"}</small></div></div>
   <nav>{nav.map(([id,label,ico])=><button key={id} className={page===id?"active":""} onClick={()=>onNavigate(id)}><span>{ico}</span>{label}</button>)}</nav>
   <div className="side-bottom"><button onClick={()=>onNavigate("support")}>? Support</button><button onClick={()=>{clearSession();onLogout()}}>↪ Sign out</button></div>
 </aside><main className="main">
   <header><div className="crumb">{page.replaceAll("-"," ")}</div><div className="header-actions">
    <button className="status" onClick={check}>● {status||"System Status"}</button>
    <button onClick={()=>setLang(lang==="English"?"العربية":"English")}>文 {lang}</button><button onClick={()=>alert("No new notifications.")}>♧</button>
    <button className="avatar" title={u?.username} onClick={()=>alert(`${u?.first_name||""} ${u?.last_name||""}\nUsername: ${u?.username}\nRole: ${u?.role}`)}>{(u?.first_name||u?.username||"U")[0].toUpperCase()}</button>
   </div></header>
   <div className="content">{children}</div>
 </main></div>
}

function ActivateAccount({onDone}){
 const [step,setStep]=useState("verify");
 const [username,setUsername]=useState("");
 const [activationCode,setActivationCode]=useState("");
 const [password,setPassword]=useState("");
 const [confirm,setConfirm]=useState("");
 const [error,setError]=useState("");
 const [loading,setLoading]=useState(false);

 async function verify(e){
  e.preventDefault(); setError("");
  if(!/^\d{6}$/.test(activationCode)){setError("Activation code must be 6 digits.");return}
  setLoading(true);
  try{await api.verifyActivation({username:username.trim(),activation_code:activationCode});setStep("password")}
  catch(e){setError(errText(e))}
  finally{setLoading(false)}
 }

 async function submitPassword(e){
  e.preventDefault(); setError("");
  if(password.length<8){setError("Password must be at least 8 characters.");return}
  if(password!==confirm){setError("Passwords do not match.");return}
  setLoading(true);
  try{await api.setupPassword({username:username.trim(),activation_code:activationCode,password});setStep("done")}
  catch(e){setError(errText(e))}
  finally{setLoading(false)}
 }

 if(step==="done")return <div className="login"><div className="login-card">
  <div className="brand center"><span className="logo">G</span><div><b>GymFlow Pro</b><small>Gym SaaS Management</small></div></div>
  <div className="alert">Account activated successfully.</div>
  <p className="muted">Your account is ready. You can now sign in with your username and new password.</p>
  <button className="primary full" onClick={onDone}>Continue to sign in</button>
 </div></div>;

 if(step==="password")return <div className="login"><div className="login-card">
  <div className="brand center"><span className="logo">G</span><div><b>GymFlow Pro</b><small>Secure account setup</small></div></div>
  <h1>Create your password</h1>
  <p className="muted">Create a password of at least 8 characters for <b>{username}</b>.</p>
  {error&&<div className="alert error">{error}</div>}
  <form onSubmit={submitPassword}>
   <label>New password<input type="password" minLength="8" value={password} onChange={e=>setPassword(e.target.value)} required autoComplete="new-password"/></label>
   <label>Confirm password<input type="password" minLength="8" value={confirm} onChange={e=>setConfirm(e.target.value)} required autoComplete="new-password"/></label>
   <button className="primary full" disabled={loading}>{loading?"Creating password…":"Create password"}</button>
  </form>
 </div></div>;

 return <div className="login"><div className="login-card">
  <div className="brand center"><span className="logo">G</span><div><b>GymFlow Pro</b><small>Gym SaaS Management</small></div></div>
  <h1>Activate your account</h1>
  <p className="muted">Use the username and 6-digit activation code provided by your administrator.</p>
  {error&&<div className="alert error">{error}</div>}
  <form onSubmit={verify}>
   <label>Username<input value={username} onChange={e=>setUsername(e.target.value)} required autoComplete="username"/></label>
   <label>Activation code<input value={activationCode} onChange={e=>setActivationCode(e.target.value.replace(/\D/g,"").slice(0,6))} inputMode="numeric" pattern="\d{6}" maxLength="6" placeholder="6 digits" required/></label>
   <button className="primary full" disabled={loading}>{loading?"Checking…":"Continue"}</button>
  </form>
  <button className="text-btn full" type="button" onClick={onDone}>Back to sign in</button>
 </div></div>
}

function Login({onLogin,onActivate}){
 const [username,setUsername]=useState("");const [password,setPassword]=useState("");const [loading,setLoading]=useState(false);const [error,setError]=useState("");
 async function submit(e){e.preventDefault();setLoading(true);setError("");try{const d=await api.login({username,password});setSession(d);onLogin(d.user)}catch(e){setError(errText(e))}finally{setLoading(false)}}
 return <div className="login"><div className="login-card"><div className="brand center"><span className="logo">G</span><div><b>GymFlow Pro</b><small>Gym SaaS Management</small></div></div><h1>Welcome back</h1><p className="muted">Sign in with your username and password.</p>{error&&<div className="alert error">{error}</div>}<form onSubmit={submit}><label>Username<input value={username} onChange={e=>setUsername(e.target.value)} required autoComplete="username"/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} required autoComplete="current-password"/></label><button className="primary full" disabled={loading}>{loading?"Signing in…":"Sign in"}</button></form><button className="text-btn full" type="button" onClick={onActivate}>First time here? Activate your account</button></div></div>
}

function Page({title,subtitle,actions,children}){return <><div className="page-head"><div><h1>{title}</h1>{subtitle&&<p>{subtitle}</p>}</div><div className="actions">{actions}</div></div>{children}</>}

function Dashboard({role,onNavigate}){
 const [data,setData]=useState(null);const [loading,setLoading]=useState(true);const [error,setError]=useState("");
 useEffect(()=>{(async()=>{try{setData(role==="saas_admin"?await api.saasDashboard():role==="staff"?await api.staffDashboard():await api.gymDashboard())}catch(e){setError(errText(e))}finally{setLoading(false)}})()},[role]);
 if(loading)return <Loading/>; if(error)return <ErrorBox text={error}/>;
 const d=data||{};
 if(role==="saas_admin") return <Page title="Dashboard" subtitle="Platform overview and SaaS performance." actions={<button className="primary" onClick={()=>onNavigate("gyms")}>＋ New Gym</button>}><Stats items={[
  ["Total Gyms",d.total_gyms||0,"store"],["Active Gyms",d.active_gyms||0,"check"],["SaaS Subscriptions",d.saas_subscriptions||0,"layers"],["SaaS Revenue",money(d.saas_revenue),"revenue"]
 ]}/><div className="grid2"><Panel title="Plan distribution"><MiniList
  items={
    Array.isArray(d.plan_distribution)
      ? d.plan_distribution.map(x => [x.plan, x.count])
      : Object.entries(d.plan_distribution || {}).map(([k, v]) => [k, v])
  }
/></Panel><Panel title="Recent subscriptions"><MiniList items={(d.recent_subscriptions||[]).slice(0,6).map(x=>[x.gym_id?.slice(0,8)||"Gym",fmt(x.start_date)])}/></Panel></div></Page>;
 return <Page title={role==="staff"?"Operational Dashboard":"Gym Dashboard"} subtitle={role==="staff"?"Today's operations at a glance.":"A real-time overview of your gym."} actions={<button className="secondary" onClick={()=>downloadFile("gymflow-dashboard.json",JSON.stringify(d,null,2))}>⇩ Download Report</button>}><Stats items={role==="staff"?[
  ["Today's Check-ins",d.todays_checkins||0,"check"],["Active Members",d.active_members||0,"members"],["Expiring Subscriptions",d.expiring_subscriptions||0,"clock"],["Recent Activity",(d.recent_activity||[]).length,"activity"]
]:[
  ["Total Members",d.total_members||0,"members"],["Active Members",d.active_members||0,"check"],["Active Subscriptions",d.active_subscriptions||0,"layers"],["Revenue",money(d.revenue),"revenue"]
]}/><div className="grid2"><Panel title="Attendance"><div className="big-number">{d.attendance||d.todays_checkins||0}</div><p className="muted">Check-ins recorded</p><button className="text-btn" onClick={()=>onNavigate("attendance")}>View attendance →</button></Panel><Panel title="Expiring subscriptions"><div className="big-number">{d.expiring_subscriptions||0}</div><p className="muted">Need attention soon</p><button className="text-btn" onClick={()=>onNavigate("subscriptions")}>View subscriptions →</button></Panel></div></Page>
}

function Stats({items}){return <div className="stats">{items.map(([a,b,c])=><div className="stat" key={a}><span className="stat-icon">{c==="revenue"?"$":c==="check"?"✓":c==="members"?"●":c==="layers"?"◆":"▣"}</span><div><small>{a}</small><strong>{b}</strong></div></div>)}</div>}
function Panel({title,children,action}){return <section className="panel"><div className="panel-head"><h3>{title}</h3>{action}</div>{children}</section>}
function MiniList({items}){return items?.length?<div className="mini-list">{items.map((x,i)=><div key={i}><span>{x[0]}</span><b>{x[1]}</b></div>)}</div>:<Empty text="No data yet."/>}
function Loading(){return <div className="loading">Loading…</div>}
function Empty({text="No records found."}){return <div className="empty">{text}</div>}
function ErrorBox({text}){return <div className="alert error">{text}</div>}

function Gyms({onNavigate}){
 const [rows,setRows]=useState([]),[open,setOpen]=useState(false),[toast,setToast]=useState(""),[filter,setFilter]=useState("");
 const load=()=>api.gyms().then(setRows).catch(e=>setToast(errText(e)));useEffect(() => {
  load();
}, []);;
 const filtered=rows.filter(x=>(x.name+" "+x.owner_name+" "+x.email).toLowerCase().includes(filter.toLowerCase()));
 return <Page title="Gyms" subtitle="Manage all gyms on the platform." actions={<button className="primary" onClick={()=>setOpen(true)}>＋ Add Gym</button>}><Toolbar value={filter} onChange={setFilter} placeholder="Search gyms…"/><Table headers={["Gym","Owner","Contact","Status","Actions"]} rows={filtered.map(g=>[<><b>{g.name}</b><small>{shortId(g.id)}…</small></>,g.owner_name,<><span>{g.email}</span><small>{g.phone||"—"}</small></>,<Badge value={g.status}/>,<div className="row-actions"><button onClick={()=>onNavigate("gym-detail",g.id)}>View</button><button onClick={async()=>{try{await api.disableGym(g.id);setToast("Gym disabled");load()}catch(e){setToast(errText(e))}}}>Disable</button></div>])}/>{open&&<GymModal onClose={()=>setOpen(false)} onSaved={()=>{setOpen(false);load()}}/>}<Toast msg={toast}/></Page>
}
function GymModal({onClose,onSaved}){
 const [form,setForm]=useState({gym:{name:"",owner_name:"",email:"",phone:"",address:""},gym_admin:{username:"",first_name:"",last_name:""}}),[error,setError]=useState("");
 const set=(section,key,v)=>setForm(f=>({...f,[section]:{...f[section],[key]:v}}));
 async function save(e){e.preventDefault();try{const d=await api.createGym(form);alert(`Gym created successfully.\n\nUsername: ${d.username}\nActivation code: ${d.activation_code}\n\nGive these details to the gym owner. The activation code can be used once.`);onSaved()}catch(e){setError(errText(e))}}
 return <Modal title="Create Gym & Gym Admin" onClose={onClose}><form className="formgrid" onSubmit={save}>{error&&<div className="alert error fullrow">{error}</div>}<h4 className="fullrow">Gym</h4>{["name","owner_name","email","phone","address"].map(k=><label key={k}>{k.replaceAll("_"," ")}<input required={["name","owner_name","email"].includes(k)} value={form.gym[k]} onChange={e=>set("gym",k,e.target.value)}/></label>)}<h4 className="fullrow">Gym Admin</h4>{["username","first_name","last_name"].map(k=><label key={k}>{k.replaceAll("_"," ")}<input required={k!=="last_name"} value={form.gym_admin[k]} onChange={e=>set("gym_admin",k,e.target.value)}/></label>)}<div className="modal-actions fullrow"><button type="button" onClick={onClose}>Cancel</button><button className="primary">Create</button></div></form></Modal>
}

function Members({role,onNavigate}){
 const [rows,setRows]=useState([]),[filter,setFilter]=useState(""),[open,setOpen]=useState(false),[toast,setToast]=useState("");
 const load=()=>api.members().then(setRows).catch(e=>setToast(errText(e)));useEffect(() => {
  load();
}, []);;
 const filtered=rows.filter(x=>(x.first_name+" "+x.last_name+" "+(x.email||"")+" "+x.phone).toLowerCase().includes(filter.toLowerCase()));
 return <Page title="Members" subtitle="Manage member profiles and activity." actions={<button className="primary" onClick={()=>setOpen(true)}>＋ Add Member</button>}><Toolbar value={filter} onChange={setFilter} placeholder="Search by name, email or phone…"/><Table headers={["Member","Contact","Status","Joined","Actions"]} rows={filtered.map(m=>[<><b>{m.first_name} {m.last_name}</b><small>{shortId(m.id)}…</small></>,<><span>{m.email||"—"}</span><small>{m.phone}</small></>,<Badge value={m.status}/>,fmt(m.joined_at),<div className="row-actions"><button onClick={()=>onNavigate("member",m.id)}>View</button><button onClick={()=>setOpen({member:m})}>Edit</button>{role==="gym_admin"&&<button onClick={async()=>{if(confirm("Delete member?")){try{await api.deleteMember(m.id);load()}catch(e){setToast(errText(e))}}}}>Delete</button>}</div>])}/>{open&&<MemberModal member={open.member} onClose={()=>setOpen(false)} onSaved={()=>{setOpen(false);load()}}/>}<Toast msg={toast}/></Page>
}
function MemberModal({member,onClose,onSaved}){
 const empty={first_name:"",last_name:"",email:"",phone:"",date_of_birth:"",gender:"",height:"",weight:""};const [f,setF]=useState(member?{...member,date_of_birth:member.date_of_birth||"",height:member.height||"",weight:member.weight||""}:empty);const [error,setError]=useState("");
 async function save(e){e.preventDefault();try{const body={...f,height:f.height?Number(f.height):null,weight:f.weight?Number(f.weight):null,date_of_birth:f.date_of_birth||null};if(member)await api.updateMember(member.id,body);else await api.createMember(body);onSaved()}catch(e){setError(errText(e))}}
 return <Modal title={member?"Edit Member":"Add New Member"} onClose={onClose} wide><form className="formgrid" onSubmit={save}>{error&&<div className="alert error fullrow">{error}</div>}{Object.keys(empty).map(k=><label key={k}>{k.replaceAll("_"," ")}<input type={k==="date_of_birth"?"date":k==="email"?"email":"text"} value={f[k]??""} onChange={e=>setF({...f,[k]:e.target.value})} required={["first_name","last_name","phone"].includes(k)}/></label>)}<div className="modal-actions fullrow"><button type="button" onClick={onClose}>Cancel</button><button className="primary">Save member</button></div></form></Modal>
}

function MemberProfile({id,onNavigate}){
 const [m,setM]=useState(null),[subs,setSubs]=useState([]),[payments,setPayments]=useState([]),[att,setAtt]=useState([]),[meas,setMeas]=useState([]),[modal,setModal]=useState(null),[toast,setToast]=useState("");
 const load=async()=>{try{const [mm,s,p,a,me]=await Promise.all([api.member(id),api.subscriptions(),api.payments(),api.attendance(),api.measurements(id)]);setM(mm);setSubs(s.filter(x=>x.member_id===id));setPayments(p.filter(x=>s.some(z=>z.id===x.subscription_id&&z.member_id===id)));setAtt(a.filter(x=>x.member_id===id));setMeas(me)}catch(e){setToast(errText(e))}};useEffect(()=>{load()},[id]);
 if(!m)return <Loading/>;
 const active=subs.find(x=>x.status==="active")||subs[0]; const activeAttendance=att.find(x=>!x.check_out_time);
 return <Page title={`${m.first_name} ${m.last_name}`} subtitle={`Member profile • ${shortId(m.id)}…`} actions={<><button className="secondary" onClick={()=>setModal("payment")}>$ Payment</button>{activeAttendance?<button className="secondary" onClick={async()=>{try{await api.checkOut(activeAttendance.id);setToast("Checked out");load()}catch(e){setToast(errText(e))}}}>✓ Check Out</button>:<button className="secondary" onClick={async()=>{try{await api.checkIn(id);setToast("Checked in");load()}catch(e){setToast(errText(e))}}}>✓ Check In</button>}<button className="secondary" onClick={()=>setModal("measurement")}>◉ Measure</button><button className="primary" onClick={()=>setModal("subscription")}>↻ Renew Sub</button></>}><div className="profile-grid"><Panel title="Profile"><div className="profile"><div className="avatar large">{(m.first_name||"?")[0]}{(m.last_name||"?")[0]}</div><div><h2>{m.first_name} {m.last_name}</h2><p>{m.email||"No email"} · {m.phone}</p><Badge value={m.status}/></div></div><div className="details">{[["Date of birth",fmt(m.date_of_birth)],["Gender",m.gender||"—"],["Height",m.height?`${m.height} cm`:"—"],["Weight",m.weight?`${m.weight} kg`:"—"],["Joined",fmt(m.joined_at)],["Last visit",fmt(m.last_visit_at)]].map(x=><div key={x[0]}><small>{x[0]}</small><b>{x[1]}</b></div>)}</div></Panel><Panel title="Current Subscription">{active?<div className="subscription-card"><h3>{shortId(active.plan_id)}…</h3><div className="details"><div><small>Status</small><b><Badge value={active.status}/></b></div><div><small>Period</small><b>{fmt(active.start_date)} — {fmt(active.end_date)}</b></div><div><small>Amount</small><b>{money(active.amount)}</b></div></div><div className="row-actions"><button onClick={()=>onNavigate("subscriptions")}>View all subscription history</button><button onClick={()=>downloadFile(`member-${m.id}.json`,JSON.stringify({member:m,subscriptions:subs,payments,attendance:att,measurements:meas},null,2))}>View Contract ↗</button></div></div>:<Empty text="No subscription yet."/>}</Panel></div><div className="grid3"><Panel title="Subscription History"><MiniList items={subs.map(s=>[s.status,fmt(s.end_date)])}/></Panel><Panel title="Payments"><MiniList items={payments.map(p=>[money(p.amount),fmt(p.payment_date)])}/></Panel><Panel title="Attendance"><MiniList items={att.slice(0,7).map(a=>[fmt(a.check_in_time),a.check_out_time?"Out":"In"])}/></Panel></div><Toast msg={toast}/>{modal==="payment"&&<PaymentModal memberId={id} subscriptions={subs} onClose={()=>setModal(null)} onSaved={()=>{setModal(null);load()}}/>}{modal==="measurement"&&<MeasurementModal memberId={id} onClose={()=>setModal(null)} onSaved={()=>{setModal(null);load()}}/>}{modal==="subscription"&&<SubscriptionModal memberId={id} onClose={()=>setModal(null)} onSaved={()=>{setModal(null);load()}}/>}</Page>
}

function SubscriptionModal({memberId,onClose,onSaved}){const today=new Date().toISOString().slice(0,10);const [plans,setPlans]=useState([]),[f,setF]=useState({plan_id:"",start_date:today,end_date:"",amount:"",auto_renew:false}),[error,setError]=useState(""),[loading,setLoading]=useState(true),[saving,setSaving]=useState(false);useEffect(()=>{let alive=true;(async()=>{try{const p=await api.plans();if(!alive)return;const list=Array.isArray(p)?p:[];setPlans(list);if(list[0])setF(x=>({...x,plan_id:list[0].id,amount:list[0].price??"",end_date:list[0].duration_months?addMonths(x.start_date||today,list[0].duration_months):""}))}catch(e){if(alive)setError(errText(e))}finally{if(alive)setLoading(false)}})();return()=>{alive=false}},[]);const choosePlan=id=>{const p=plans.find(x=>x.id===id);setF(x=>({...x,plan_id:id,amount:p?.price??"",end_date:p?.duration_months?addMonths(x.start_date||today,p.duration_months):""}))};const chooseStart=start=>{const p=plans.find(x=>x.id===f.plan_id);setF(x=>({...x,start_date:start,end_date:p?.duration_months?addMonths(start,p.duration_months):x.end_date}))};async function save(e){e.preventDefault();setError("");if(!f.plan_id){setError("Please select a membership plan.");return}if(!f.start_date||!f.end_date){setError("Please select valid start and end dates.");return}setSaving(true);try{await api.createSubscription({member_id:memberId,...f,amount:Number(f.amount)});onSaved()}catch(e){setError(errText(e))}finally{setSaving(false)}}return <Modal title="Create / Renew Subscription" onClose={onClose}><form onSubmit={save}>{error&&<div className="alert error">{error}</div>}{loading?<p className="muted">Loading membership plans…</p>:!plans.length?<div className="alert error">No membership plans are available. Create a plan first.</div>:<><label>Plan<select value={f.plan_id} onChange={e=>choosePlan(e.target.value)} required>{plans.map(p=><option key={p.id} value={p.id}>{p.name} — {money(p.price)}</option>)}</select></label><label>Start date<input type="date" value={f.start_date} onChange={e=>chooseStart(e.target.value)} required/></label><label>End date<input type="date" value={f.end_date} onChange={e=>setF({...f,end_date:e.target.value})} required/></label><label>Amount<input type="number" min="0" step="0.01" value={f.amount} onChange={e=>setF({...f,amount:e.target.value})} required/></label><label className="checkline"><input type="checkbox" checked={!!f.auto_renew} onChange={e=>setF({...f,auto_renew:e.target.checked})}/> Auto renew</label><button className="primary full" disabled={saving}>{saving?"Saving…":"Save subscription"}</button></>}</form></Modal>}

function PaymentModal({memberId,subscriptions,onClose,onSaved}){
 const [f,setF]=useState({subscription_id:subscriptions[0]?.id||"",amount:subscriptions[0]?.amount||"",payment_method:"cash"}),[error,setError]=useState(""),[saving,setSaving]=useState(false);
 async function save(e){e.preventDefault();setError("");if(!f.subscription_id){setError("Please select a subscription.");return}if(f.amount===""||Number.isNaN(Number(f.amount))){setError("Please enter a valid amount.");return}setSaving(true);try{await api.createPayment({...f,amount:Number(f.amount)});onSaved()}catch(e){setError(errText(e))}finally{setSaving(false)}}
 return <Modal title="Record Payment" onClose={onClose}><form onSubmit={save}>{error&&<div className="alert error">{error}</div>}<label>Subscription<select value={f.subscription_id} onChange={e=>{const id=e.target.value;const sub=subscriptions.find(x=>x.id===id);setF({...f,subscription_id:id,amount:sub?.amount??""})}} required disabled={!subscriptions.length}>{subscriptions.length?subscriptions.map(s=><option key={s.id} value={s.id}>{fmt(s.start_date)} — {fmt(s.end_date)} · {money(s.amount)}</option>):<option value="">No subscriptions available</option>}</select></label>{!subscriptions.length&&<div className="alert error">Create a subscription first, then record its payment.</div>}<label>Amount<input type="number" min="0" step="0.01" value={f.amount} onChange={e=>setF({...f,amount:e.target.value})} required/></label><label>Payment method<select value={f.payment_method} onChange={e=>setF({...f,payment_method:e.target.value})}><option value="cash">Cash</option><option value="card">Card</option><option value="bank_transfer">Bank transfer</option></select></label><button className="primary full" disabled={saving||!subscriptions.length}>{saving?"Recording…":"Record payment"}</button></form></Modal>}

function MeasurementModal({memberId,measurement,onClose,onSaved}){
 const [f,setF]=useState(measurement?{weight:measurement.weight??"",body_fat_percentage:measurement.body_fat_percentage??"",bmi:measurement.bmi??"",notes:measurement.notes??""}:{weight:"",body_fat_percentage:"",bmi:"",notes:""}),[error,setError]=useState(""),[saving,setSaving]=useState(false);
 async function save(e){e.preventDefault();setError("");setSaving(true);try{const body={weight:f.weight!==""?Number(f.weight):null,body_fat_percentage:f.body_fat_percentage!==""?Number(f.body_fat_percentage):null,bmi:f.bmi!==""?Number(f.bmi):null,notes:f.notes||null};if(measurement)await api.updateMeasurement(memberId,measurement.id,body);else await api.createMeasurement(memberId,body);onSaved()}catch(e){setError(errText(e))}finally{setSaving(false)}}
 return <Modal title={measurement?"Edit Measurement":"Record Measurement"} onClose={onClose}><form onSubmit={save}>{error&&<div className="alert error">{error}</div>}<label>Weight<input type="number" min="0" step="0.01" value={f.weight} onChange={e=>setF({...f,weight:e.target.value})}/></label><label>Body fat percentage<input type="number" min="0" max="100" step="0.1" value={f.body_fat_percentage} onChange={e=>setF({...f,body_fat_percentage:e.target.value})}/></label><label>BMI<input type="number" min="0" step="0.1" value={f.bmi} onChange={e=>setF({...f,bmi:e.target.value})}/></label><label>Notes<input value={f.notes} onChange={e=>setF({...f,notes:e.target.value})}/></label><button className="primary full" disabled={saving}>{saving?"Saving…":measurement?"Save changes":"Save measurement"}</button></form></Modal>}


function Staff({onNavigate}){const [rows,setRows]=useState([]),[open,setOpen]=useState(false),[toast,setToast]=useState("");const load=()=>api.staff().then(x=>setRows(Array.isArray(x)?x:[])).catch(e=>setToast(errText(e)));useEffect(() => {
  load();
}, []);return <Page title="Staff" subtitle="Manage staff accounts for your gym." actions={<button className="primary" onClick={()=>setOpen(true)}>＋ Add Staff</button>}><Table headers={["Staff","Position","Status","Actions"]} rows={rows.map(s=>[<b>{s.username||s.user_id?.slice(0,8)||"—"}…</b>,s.position||"—",<Badge value={s.status}/>,<div className="row-actions"><button onClick={()=>setOpen({staff:s})}>Edit</button><button onClick={async()=>{try{await api.disableStaff(s.id);load()}catch(e){setToast(errText(e))}}}>Disable</button></div>])}/>{open&&<StaffModal staff={open.staff} onClose={()=>setOpen(false)} onSaved={()=>{setOpen(false);load()}}/>}<Toast msg={toast}/></Page>}
function StaffModal({staff,onClose,onSaved}){const [f,setF]=useState(staff?{position:staff.position,status:staff.status}:{username:"",first_name:"",last_name:"",position:""}),[error,setError]=useState("");async function save(e){e.preventDefault();try{if(staff)await api.updateStaff(staff.id,f);else{const d=await api.createStaff(f);alert(`Staff created successfully.\n\nUsername: ${d.username}\nActivation code: ${d.activation_code}\n\nGive these details to the staff member. The activation code can be used once.`)}onSaved()}catch(e){setError(errText(e))}}return <Modal title={staff?"Edit Staff":"Create Staff"} onClose={onClose}><form onSubmit={save}>{error&&<div className="alert error">{error}</div>}{Object.keys(f).map(k=><label key={k}>{k.replaceAll("_"," ")}<input value={f[k]??""} onChange={e=>setF({...f,[k]:e.target.value})} required={k==="username"||k==="first_name"||k==="position"}/></label>)}<button className="primary full">Save</button></form></Modal>}

function Plans(){const [rows,setRows]=useState([]),[open,setOpen]=useState(false),[toast,setToast]=useState("");const load=()=>api.plans().then(setRows).catch(e=>setToast(errText(e)));useEffect(() => {
  load();
}, []);;return <Page title="Plans" subtitle="Membership plans offered by your gym." actions={<button className="primary" onClick={()=>setOpen(true)}>＋ New Plan</button>}><Table headers={["Plan","Price","Duration","Status","Actions"]} rows={rows.map(p=>[<><b>{p.name}</b><small>{p.description||"—"}</small></>,money(p.price),`${p.duration_months} months`,<Badge value={p.status}/>,<div className="row-actions"><button onClick={()=>setOpen(p)}>Edit</button><button onClick={async()=>{try{await api.deletePlan(p.id);load()}catch(e){setToast(errText(e))}}}>Delete</button></div>])}/>{open&&<PlanModal plan={open===true?null:open} onClose={()=>setOpen(false)} onSaved={()=>{setOpen(false);load()}}/>}<Toast msg={toast}/></Page>}
function PlanModal({plan,onClose,onSaved}){const [f,setF]=useState(plan?{...plan}:{name:"",description:"",price:"",duration_months:1}),[error,setError]=useState("");async function save(e){e.preventDefault();try{const body={...f,price:Number(f.price),duration_months:Number(f.duration_months)};plan?await api.updatePlan(plan.id,body):await api.createPlan(body);onSaved()}catch(e){setError(errText(e))}}return <Modal title={plan?"Edit Plan":"New Plan"} onClose={onClose}><form onSubmit={save}>{error&&<div className="alert error">{error}</div>}{["name","description","price","duration_months"].map(k=><label key={k}>{k.replaceAll("_"," ")}<input type={k==="price"?"number":"text"} value={f[k]??""} onChange={e=>setF({...f,[k]:e.target.value})} required={k==="name"||k==="price"}/></label>)}<button className="primary full">Save plan</button></form></Modal>}

function DataList({kind}){
 const [rows,setRows]=useState([]),[members,setMembers]=useState([]),[plans,setPlans]=useState([]),[paymentSubs,setPaymentSubs]=useState([]),[open,setOpen]=useState(false),[toast,setToast]=useState(""),[loading,setLoading]=useState(true);
 const load=async()=>{setLoading(true);try{if(kind==="subscriptions"){const [subs,ms,ps]=await Promise.all([api.subscriptions(),api.members(),api.plans()]);setRows(Array.isArray(subs)?subs:[]);setMembers(Array.isArray(ms)?ms:[]);setPlans(Array.isArray(ps)?ps:[])}else if(kind==="payments"){const [pay,subs,ms,ps]=await Promise.all([api.payments(),api.subscriptions(),api.members(),api.plans()]);setRows(Array.isArray(pay)?pay:[]);setMembers(Array.isArray(ms)?ms:[]);setPlans(Array.isArray(ps)?ps:[]);setPaymentSubs(Array.isArray(subs)?subs:[])}else{const a=await api.attendance();setRows(Array.isArray(a)?a:[])}}catch(e){setToast(errText(e))}finally{setLoading(false)}};
 useEffect(()=>{load()},[kind]); const title=kind[0].toUpperCase()+kind.slice(1);
 const safeRows=rows.map(r=>{if(kind==="subscriptions"){const m=members.find(x=>x.id===r.member_id),p=plans.find(x=>x.id===r.plan_id);return [m?`${m.first_name} ${m.last_name}`:shortId(r.member_id),p?.name||shortId(r.plan_id),`${fmt(r.start_date)} — ${fmt(r.end_date)}`,money(r.amount),<Badge value={r.status}/>,<button onClick={()=>setOpen(r)}>Edit</button>]}if(kind==="payments"){const sub=paymentSubs.find(x=>x.id===r.subscription_id),m=sub&&members.find(x=>x.id===sub.member_id),p=sub&&plans.find(x=>x.id===sub.plan_id);return [m?`${m.first_name} ${m.last_name}`:shortId(r.subscription_id)+"…",p?.name||"Subscription",money(r.amount),r.payment_method||"—",<Badge value={r.status}/>,fmt(r.payment_date)]}return [shortId(r.member_id)+"…",fmt(r.check_in_time),fmt(r.check_out_time),<Badge value={r.check_out_time?"completed":"active"}/>,!r.check_out_time?<button onClick={async()=>{try{await api.checkOut(r.id);setToast("Member checked out");load()}catch(e){setToast(errText(e))}}}>Check out</button>:<span className="muted">Completed</span>]});
 const paymentAction=kind==="payments"?<button className="primary" onClick={()=>setOpen(true)}>＋ Record Payment</button>:kind==="subscriptions"?<button className="primary" onClick={()=>setOpen(true)}>＋ New Subscription</button>:null;
 return <Page title={title} subtitle={`Manage ${kind} for the current gym.`} actions={paymentAction}>{loading?<Loading/>:<Table headers={kind==="subscriptions"?["Member","Plan","Period","Amount","Status","Actions"]:kind==="payments"?["Member","Plan","Amount","Method","Status","Date"]:["Member","Check in","Check out","Status","Action"]} rows={safeRows}/>} {open&&kind==="subscriptions"&&<SubscriptionEdit sub={open===true?null:open} members={members} plans={plans} onClose={()=>setOpen(false)} onSaved={()=>{setOpen(false);load()}}/>}{open&&kind==="payments"&&<PaymentModal memberId={null} subscriptions={paymentSubs} onClose={()=>setOpen(false)} onSaved={()=>{setOpen(false);load()}}/>}<Toast msg={toast}/></Page>}

function SubscriptionEdit({sub,members,plans,onClose,onSaved}){
 const today=new Date().toISOString().slice(0,10);
 const [f,setF]=useState(sub?{status:sub.status,end_date:sub.end_date||"",amount:sub.amount??0,auto_renew:!!sub.auto_renew}:{member_id:"",plan_id:"",start_date:today,end_date:"",amount:"",auto_renew:false});
 const [error,setError]=useState(""); const [saving,setSaving]=useState(false);
 useEffect(()=>{if(sub)return;const firstMember=members?.[0],firstPlan=plans?.[0];setF(x=>{const plan=plans?.find(p=>p.id===x.plan_id)||firstPlan;const start=x.start_date||today;return {...x,member_id:x.member_id||firstMember?.id||"",plan_id:x.plan_id||plan?.id||"",amount:x.amount!==""&&x.amount!=null?x.amount:(plan?.price??""),end_date:x.end_date||(plan?.duration_months?addMonths(start,plan.duration_months):"")}})},[sub,members,plans]);
 const choosePlan=(planId)=>{const p=plans.find(x=>x.id===planId);setF(x=>({...x,plan_id:planId,amount:p?.price??"",end_date:p?.duration_months?addMonths(x.start_date||today,p.duration_months):""}))};
 const chooseStart=(start)=>{const p=plans.find(x=>x.id===f.plan_id);setF(x=>({...x,start_date:start,end_date:p?.duration_months?addMonths(start,p.duration_months):x.end_date}))};
 async function save(e){e.preventDefault();setError("");if(!sub&&(!f.member_id||!f.plan_id)){setError("Please select a member and a plan.");return}if(!f.start_date||!f.end_date){setError("Please select valid start and end dates.");return}if(f.amount===""||Number.isNaN(Number(f.amount))){setError("Please enter a valid amount.");return}setSaving(true);try{if(sub)await api.updateSubscription(sub.id,{...f,amount:Number(f.amount)});else await api.createSubscription({...f,amount:Number(f.amount)});onSaved()}catch(e){setError(errText(e))}finally{setSaving(false)}}
 const hasPlans=Array.isArray(plans)&&plans.length>0;
 return <Modal title={sub?"Update Subscription":"New Subscription"} onClose={onClose}><form onSubmit={save}>{error&&<div className="alert error">{error}</div>}{!sub&&<><label>Member<select value={f.member_id} onChange={e=>setF({...f,member_id:e.target.value})} required disabled={!members?.length}>{members?.map(m=><option key={m.id} value={m.id}>{m.first_name} {m.last_name}</option>)}</select></label><label>Plan<select value={f.plan_id} onChange={e=>choosePlan(e.target.value)} required disabled={!hasPlans}>{hasPlans?plans.map(p=><option key={p.id} value={p.id}>{p.name} — {money(p.price)}</option>):<option value="">No plans available</option>}</select></label>{!hasPlans&&<div className="alert error">No membership plans are available. Create a plan first, then create the subscription.</div>}<label>Start date<input type="date" value={f.start_date} onChange={e=>chooseStart(e.target.value)} required/></label></>}{<label>End date<input type="date" value={f.end_date} onChange={e=>setF({...f,end_date:e.target.value})} required/></label>}<label>Amount<input type="number" min="0" step="0.01" value={f.amount} onChange={e=>setF({...f,amount:e.target.value})} required/></label>{sub&&<label>Status<select value={f.status||"active"} onChange={e=>setF({...f,status:e.target.value})}><option value="active">active</option><option value="expired">expired</option><option value="cancelled">cancelled</option></select></label>}<label className="checkline"><input type="checkbox" checked={!!f.auto_renew} onChange={e=>setF({...f,auto_renew:e.target.checked})}/> Auto renew</label><button className="primary full" disabled={saving||(!sub&&!hasPlans)||(!sub&&!members?.length)}>{saving?"Saving…":"Save subscription"}</button></form></Modal>}

function Measurements(){const [members,setMembers]=useState([]),[id,setId]=useState(""),[rows,setRows]=useState([]),[open,setOpen]=useState(false),[toast,setToast]=useState("");const load=async()=>{try{const m=await api.members();setMembers(Array.isArray(m)?m:[]);const selected=id||m?.[0]?.id||"";if(!id&&selected)setId(selected);if(selected){const data=await api.measurements(selected);setRows(Array.isArray(data)?data:[])}}catch(e){setToast(errText(e))}};useEffect(()=>{load()},[]);useEffect(()=>{if(!id)return;api.measurements(id).then(x=>setRows(Array.isArray(x)?x:[])).catch(e=>setToast(errText(e)))},[id]);return <Page title="Measurements" subtitle="Track member body measurements over time." actions={<button className="primary" onClick={()=>setOpen(true)} disabled={!id}>＋ Record</button>}><div className="filterbar"><label>Member<select value={id} onChange={e=>setId(e.target.value)} disabled={!members.length}>{members.map(m=><option key={m.id} value={m.id}>{m.first_name} {m.last_name}</option>)}</select></label></div><Table headers={["Measured","Weight","Body Fat","BMI","Notes","Actions"]} rows={rows.map(x=>[fmt(x.measured_at),x.weight!=null?`${x.weight} kg`:"—",x.body_fat_percentage!=null?`${x.body_fat_percentage}%`:"—",x.bmi!=null?x.bmi:"—",x.notes||"—",<button onClick={()=>setOpen(x)}>Edit</button>])}/>{open&&<MeasurementModal memberId={id} measurement={open===true?null:open} onClose={()=>setOpen(false)} onSaved={async()=>{setOpen(false);try{setRows(await api.measurements(id))}catch(e){setToast(errText(e))}}}/>}<Toast msg={toast}/></Page>}

function Attendance(){const [rows,setRows]=useState([]),[members,setMembers]=useState([]),[id,setId]=useState(""),[toast,setToast]=useState("");const load=async()=>{try{const [a,m]=await Promise.all([api.attendance(),api.members()]);setRows(Array.isArray(a)?a:[]);setMembers(Array.isArray(m)?m:[]);if(m?.[0]&&!id)setId(m[0].id)}catch(e){setToast(errText(e))}};useEffect(()=>{load()},[]);const selectedActive=rows.some(a=>a.member_id===id&&!a.check_out_time);return <Page title="Attendance" subtitle="Check members in and out." actions={<button className="primary" disabled={!id||selectedActive} onClick={async()=>{try{await api.checkIn(id);setToast("Member checked in");load()}catch(e){setToast(errText(e))}}}>{selectedActive?"✓ Checked In":"✓ Check In"}</button>}><div className="filterbar"><label>Member to check in<select value={id} onChange={e=>setId(e.target.value)}>{members.map(m=><option key={m.id} value={m.id}>{m.first_name} {m.last_name}</option>)}</select></label></div><Table headers={["Member","Check in","Check out","Status","Action"]} rows={rows.map(a=>[shortId(a.member_id)+"…",fmt(a.check_in_time),fmt(a.check_out_time),<Badge value={a.check_out_time?"completed":"active"}/>,!a.check_out_time?<button onClick={async()=>{try{await api.checkOut(a.id);setToast("Member checked out");load()}catch(e){setToast(errText(e))}}}>Check out</button>:<span className="muted">Completed</span>])}/><Toast msg={toast}/></Page>}

function Settings({role}){const [gym,setGym]=useState(null),[f,setF]=useState(null),[toast,setToast]=useState("");useEffect(()=>{if(role!=="gym_admin")return;let alive=true;(async()=>{try{const x=await api.getGym();if(alive){setGym(x);setF(x)}}catch(e){if(alive)setToast(errText(e))}})();return()=>{alive=false}},[role]);if(role==="saas_admin")return <Page title="Settings" subtitle="Platform settings and API connectivity."><Panel title="Backend connection"><p>API is configured through <code>VITE_API_URL</code>.</p><button className="secondary" onClick={async()=>{try{await api.health();setToast("Backend is online")}catch(e){setToast(errText(e))}}}>Test connection</button></Panel><Toast msg={toast}/></Page>;if(!f)return <Loading/>;return <Page title="Gym Settings" subtitle="Update your gym information."><Panel title="Gym information"><form className="formgrid" onSubmit={async e=>{e.preventDefault();try{const x=await api.updateGym(f);setGym(x);setToast("Saved")}catch(e){setToast(errText(e))}}}>{["name","owner_name","email","phone","address"].map(k=><label key={k}>{k.replaceAll("_"," ")}<input value={f[k]||""} onChange={e=>setF({...f,[k]:e.target.value})}/></label>)}<button className="primary">Save changes</button></form></Panel><Toast msg={toast}/></Page>}

function Support(){return <Page title="Support" subtitle="GymFlow Pro API support."><Panel title="Need help?"><p className="muted">Use the API documentation to inspect every endpoint and schema.</p><button className="primary" onClick={()=>window.open(`${location.protocol}//${location.hostname}:8000/docs`,"_blank")}>Open API Docs</button></Panel></Page>}

function Toolbar({value,onChange,placeholder}){return <div className="toolbar"><input placeholder={placeholder} value={value} onChange={e=>onChange(e.target.value)}/><button onClick={()=>onChange("")}>Clear</button></div>}
function Table({headers,rows}){return <div className="table-wrap"><table><thead><tr>{headers.map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{rows.length?rows.map((r,i)=><tr key={i}>{r.map((c,j)=><td key={j}>{c}</td>)}</tr>):<tr><td colSpan={headers.length}><Empty/></td></tr>}</tbody></table></div>}
function Badge({value}){return <span className={"badge "+String(value||"").toLowerCase().replaceAll(" ","-")}>{value||"—"}</span>}

function App(){
 const [u,setU]=useState(user()),[page,setPage]=useState("dashboard"),[param,setParam]=useState(null),[activating,setActivating]=useState(false);
 if(activating)return <ActivateAccount onDone={()=>setActivating(false)}/>;
 if(!token()||!u)return <Login onLogin={x=>{setU(x);setPage("dashboard")}} onActivate={()=>setActivating(true)}/>;
 const go=(p,id=null)=>{setPage(p);setParam(id)};
 let content;
 if(page==="dashboard")content=<Dashboard role={u.role} onNavigate={go}/>;
 else if(page==="gyms")content=<Gyms onNavigate={go}/>;
 else if(page==="member")content=<MemberProfile id={param} onNavigate={go}/>;
 else if(page==="members")content=<Members role={u.role} onNavigate={go}/>;
 else if(page==="staff")content=<Staff onNavigate={go}/>;
 else if(page==="plans")content=<Plans/>;
 else if(page==="subscriptions")content=<DataList kind="subscriptions"/>;
 else if(page==="payments")content=<DataList kind="payments"/>;
 else if(page==="attendance")content=<Attendance/>;
 else if(page==="measurements")content=<Measurements/>;
 else if(page==="settings")content=<Settings role={u.role}/>;
 else if(page==="support")content=<Support/>;
 else if(page==="saas-plans")content=<SaaSPlans/>;
 else if(page==="gym-subs")content=<GymSubs/>;
 else content=<Dashboard role={u.role} onNavigate={go}/>;
 return <Shell role={u.role} page={page} onNavigate={go} onLogout={()=>setU(null)}>{content}</Shell>
}
function SaaSPlans(){const [rows,setRows]=useState([]),[open,setOpen]=useState(false),[toast,setToast]=useState("");const load=()=>api.saasPlans().then(setRows).catch(e=>setToast(errText(e)));useEffect(() => {
  load();
}, []);;return <Page title="SaaS Plans" subtitle="Manage plans sold to gyms." actions={<button className="primary" onClick={()=>setOpen(true)}>＋ New SaaS Plan</button>}><Table headers={["Plan","Price","Max members","Actions"]} rows={rows.map(p=>[<><b>{p.name}</b><small>{p.description||"—"}</small></>,money(p.price),p.max_members_per_gym||"Unlimited",<button onClick={()=>setOpen(p)}>Edit</button>])}/>{open&&<SaasPlanModal plan={open===true?null:open} onClose={()=>setOpen(false)} onSaved={()=>{setOpen(false);load()}}/>}<Toast msg={toast}/></Page>}
function SaasPlanModal({plan,onClose,onSaved}){const [f,setF]=useState(plan?{...plan}:{name:"",description:"",price:"",max_members_per_gym:""}),[error,setError]=useState("");async function save(e){e.preventDefault();try{const body={...f,price:Number(f.price),max_members_per_gym:f.max_members_per_gym?Number(f.max_members_per_gym):null};plan?await api.updateSaasPlan(plan.id,body):await api.createSaasPlan(body);onSaved()}catch(e){setError(errText(e))}}return <Modal title={plan?"Edit SaaS Plan":"New SaaS Plan"} onClose={onClose}><form onSubmit={save}>{error&&<div className="alert error">{error}</div>}{["name","description","price","max_members_per_gym"].map(k=><label key={k}>{k.replaceAll("_"," ")}<input type={k==="price"||k==="max_members_per_gym"?"number":"text"} value={f[k]??""} onChange={e=>setF({...f,[k]:e.target.value})} required={k==="name"||k==="price"}/></label>)}<button className="primary full">Save plan</button></form></Modal>}
function GymSubs(){const [rows,setRows]=useState([]),[gyms,setGyms]=useState([]),[plans,setPlans]=useState([]),[open,setOpen]=useState(false),[toast,setToast]=useState("");const load=async()=>{try{const [s,g,p]=await Promise.all([api.gymSubs(),api.gyms(),api.saasPlans()]);setRows(s);setGyms(g);setPlans(p)}catch(e){setToast(errText(e))}};useEffect(() => {
  load();
}, []);;return <Page title="Gym Subscriptions" subtitle="Manage platform subscriptions for each gym." actions={<button className="primary" onClick={()=>setOpen(true)}>＋ New Subscription</button>}><Table headers={["Gym","Plan","Period","Status","Actions"]} rows={rows.map(s=>[gyms.find(g=>g.id===s.gym_id)?.name||shortId(s.gym_id),plans.find(p=>p.id===s.saas_plan_id)?.name||shortId(s.saas_plan_id),`${fmt(s.start_date)} — ${fmt(s.end_date)}`,<Badge value={s.status}/>,<button onClick={()=>setOpen(s)}>Edit</button>])}/>{open&&<GymSubModal sub={open===true?null:open} gyms={gyms} plans={plans} onClose={()=>setOpen(false)} onSaved={()=>{setOpen(false);load()}}/>}<Toast msg={toast}/></Page>}
function GymSubModal({sub,gyms,plans,onClose,onSaved}){const [f,setF]=useState(sub?{...sub}:{gym_id:gyms[0]?.id||"",saas_plan_id:plans[0]?.id||"",start_date:new Date().toISOString().slice(0,10),end_date:""}),[error,setError]=useState("");async function save(e){e.preventDefault();try{if(sub)await api.updateGymSub(sub.id,f);else await api.createGymSub(f);onSaved()}catch(e){setError(errText(e))}}return <Modal title={sub?"Update Gym Subscription":"New Gym Subscription"} onClose={onClose}><form onSubmit={save}>{error&&<div className="alert error">{error}</div>}<label>Gym<select value={f.gym_id} disabled={!!sub} onChange={e=>setF({...f,gym_id:e.target.value})}>{gyms.map(g=><option key={g.id} value={g.id}>{g.name}</option>)}</select></label><label>SaaS plan<select value={f.saas_plan_id} onChange={e=>setF({...f,saas_plan_id:e.target.value})}>{plans.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label><label>Start date<input type="date" value={f.start_date} onChange={e=>setF({...f,start_date:e.target.value})}/></label><label>End date<input type="date" value={f.end_date} onChange={e=>setF({...f,end_date:e.target.value})}/></label>{sub&&<label>Status<select value={f.status} onChange={e=>setF({...f,status:e.target.value})}><option>active</option><option>expired</option><option>cancelled</option></select></label>}<button className="primary full">Save</button></form></Modal>}
class AppErrorBoundary extends React.Component{constructor(props){super(props);this.state={error:null}}static getDerivedStateFromError(error){return {error}}componentDidCatch(error,info){console.error("GymFlow UI error",error,info)}render(){if(this.state.error)return <div className="login"><div className="login-card"><div className="brand center"><span className="logo">G</span><div><b>GymFlow Pro</b><small>Gym SaaS Management</small></div></div><h1>Something went wrong</h1><p className="muted">This page could not be displayed. Your data is safe.</p><div className="alert error">{this.state.error?.message||"Unexpected UI error"}</div><button className="primary full" onClick={()=>window.location.reload()}>Reload</button></div></div>;return this.props.children}}createRoot(document.getElementById("root")).render(<AppErrorBoundary><App/></AppErrorBoundary>);
