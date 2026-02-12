const actualBtn = document.getElementById('actl-btn');

const fileChosen = document.getElementById('file-chosen');

actualBtn.addEventListener('change', function(){
   if (this.files.length == 1){
        fileChosen.textContent = this.files[0].name;
   }
   else{
        fileChosen.textContent = this.files.length + " files selected";
   }

})