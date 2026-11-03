/* Auditoría de maquetación con Chrome real, sin cambios en el sitio. */
const {chromium} = require('playwright-core');
const fs = require('node:fs');
const BROWSER = process.env.CHROME_BIN || ['/usr/bin/google-chrome','/usr/bin/chromium'].find(p=>fs.existsSync(p));
const TARGETS=[
  {path:'/relojes/',selector:'#gp-collections-grid > .card',min:2},
  {path:'/bodas/',selector:'#productos > .card',min:2},
  {path:'/15-anos/',selector:'#productos > .card',min:2},
  {path:'/invitaciones/',selector:'.grid > .card',min:2},
  {path:'/invitaciones/baby-shower/',selector:'#productos > .card',min:2},
  {path:'/buscar/',selector:'#productos > .card',min:2},
];
(async()=>{
 let browser;
 const results=[];
 try{
  browser=await chromium.launch({executablePath:BROWSER,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
  for (const width of [360,390,480]){
   for(const item of TARGETS){
    const page=await browser.newPage({viewport:{width,height:820},deviceScaleFactor:1});
    const url='https://guanaprints.com'+item.path;
    try {
     const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:30000});
     await page.waitForTimeout(350);
     const metric=await page.evaluate(selector=>{
      const visible=e=>!e.hidden&&getComputedStyle(e).display!=='none';
      const cards=[...document.querySelectorAll(selector)].filter(visible);
      const first=cards[0]?.getBoundingClientRect(),second=cards[1]?.getBoundingClientRect();
      const btn=document.querySelector('.floating-whatsapp');
      const b=btn?.getBoundingClientRect();
      const cs=btn&&getComputedStyle(btn);
      return {
       width:window.innerWidth,documentWidth:document.documentElement.scrollWidth,
       cards:cards.length,stacked:!!(first&&second&&second.top>=first.bottom-1),
       whatsappVisible:!!(btn&&cs.visibility!=='hidden'&&cs.display!=='none'&&
        parseFloat(cs.opacity)>0&&cs.position==='fixed'&&b.width>0&&b.height>0&&
        b.left>=-1&&b.right<=window.innerWidth+1&&b.bottom<=window.innerHeight+1),
      };
     },item.selector);
     const passed=response?.status()===200 && metric.cards>=item.min &&
       metric.stacked && metric.documentWidth<=width+1 && metric.whatsappVisible;
     results.push({page:item.path,width,passed,...metric,status:response?.status()});
    }catch(error){results.push({page:item.path,width,passed:false,error:String(error).slice(0,200)});}
    finally{await page.close();}
   }
  }
 }catch(error){results.push({passed:false,error:'No se pudo iniciar Chrome: '+String(error).slice(0,240)});}
 finally{if(browser)await browser.close();}
 const failed=results.filter(x=>!x.passed);
 console.log(JSON.stringify({total:results.length,passed:results.length-failed.length,
   failed:failed.length,failures:failed,summary:failed.length?'REVISAR MAQUETACIÓN':'APROBADO'},null,2));
 // Esta prueba es diagnóstica y no detiene el despliegue.
})();
