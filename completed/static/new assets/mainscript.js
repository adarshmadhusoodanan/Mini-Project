//humburger bar

let navbar = document.querySelector('.header .navbar')

document.querySelector('#menu').onclick = () =>{
    navbar.classList.add('active');

}
document.querySelector('#close').onclick = () =>{
    navbar.classList.remove('active');

}


// landing motions

gsap.from('.navbar .nav_item',{opacity: 0, duration: 1, delay: 2.1, y:30, stagger: 0.2})

gsap.from('.title',{opacity: 0, duration: 1, delay: 1.6, y:30})
gsap.from('.description',{opacity: 0, duration: 1, delay: 1.8, y:30})
gsap.from('.btn',{opacity: 0, duration: 1, delay: 2.1, y:30})
gsap.from('.image',{opacity: 0, duration: 1, delay: 2.3, y:30})
gsap.from(' .projects .content',{opacity: 0, duration: 1, delay: 1.8, y:30})
gsap.from('.body .projects',{opacity: 0, duration: 1, delay: 1.8, y:30})
gsap.from('.body .contact',{opacity: 0, duration: 1, delay: 1.8, y:30})
gsap.from('.contact .content',{opacity: 0, duration: 1, delay: 1.8, y:30})