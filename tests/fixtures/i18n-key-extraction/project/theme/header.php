<?php
/**
 * Theme header. "This comment should be ignored by the scanner."
 */
$menu_label = __( 'Main menu', 'shopbd' );
?>
<nav aria-label="<?php echo esc_attr( $menu_label ); ?>">
  <a href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php esc_html_e( 'Home', 'shopbd' ); ?></a>
  <span class="cart-count">Your cart</span>
</nav>
<?php
echo 'Free delivery inside Dhaka';
$args = array( 'post_type' => 'product', 'orderby' => 'date' );
_e( 'Search products' );
echo esc_html__( 'Track your order', 'wrong-domain' );
add_action( 'wp_footer', 'shopbd_footer' );
echo '<p>' . 'সকল পণ্যে ১০% ছাড়' . '</p>';
