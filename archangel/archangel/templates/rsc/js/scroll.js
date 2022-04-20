function jumpToElement(pageElement) {    
    var positionX = 0,         
        positionY = 0;    

    while(pageElement != null){        
        positionX += pageElement.offsetLeft;        
        positionY += pageElement.offsetTop;        
        pageElement = pageElement.offsetParent;   
        options = {
            left: positionX,
            top: positionY
        }     
        window.scrollTo(options);    
    }
}
function jumpToId(elementId) {   
    pageElement = document.getElementById(elementId);
    var positionX = 0,         
        positionY = 0;    

    while(pageElement != null){        
        positionX += pageElement.offsetLeft;        
        positionY += pageElement.offsetTop;        
        pageElement = pageElement.offsetParent;    
        options = {
            left: positionX,
            top: positionY
        }      
        window.scrollTo(options);    
    }
}
function scrollToElement(pageElement) {   
    var positionX = 0,         
        positionY = 0;    

    while(pageElement != null){        
        positionX += pageElement.offsetLeft;        
        positionY += pageElement.offsetTop;        
        pageElement = pageElement.offsetParent;    
        options = {
            left: positionX,
            top: positionY,
            behavior: 'smooth'
        }      
        window.scrollTo(options);    
    }
}
function scrollToId(elementId) {   
    pageElement = document.getElementById(elementId);
    var positionX = 0,         
        positionY = 0;    

    while(pageElement != null){        
        positionX += pageElement.offsetLeft;        
        positionY += pageElement.offsetTop;        
        pageElement = pageElement.offsetParent;    
        options = {
            left: positionX,
            top: positionY,
            behavior: 'smooth'
        }      
        window.scrollTo(options);    
    }
}