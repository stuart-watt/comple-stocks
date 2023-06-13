terraform {
 backend "gcs" {
   bucket  = "comple-terraform-stacks"
   prefix  = "stock_prompter"
 }
}
