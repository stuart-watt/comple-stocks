terraform {
 backend "gcs" {
   bucket  = "my-terraform-stacks"
   prefix  = "stock_prompter"
 }
}